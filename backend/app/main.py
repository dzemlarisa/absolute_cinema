import jwt
from fastapi import FastAPI, Depends, HTTPException, Path, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import text, create_engine
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, validator
from passlib.context import CryptContext
from jwt.exceptions import PyJWTError
import pytz

import os
print("=== DEBUG DATABASE ===")
print("DATABASE_URL from env:", os.getenv("DATABASE_URL"))
print("=" * 50)

from database import get_db, DATABASE_URL
print("DATABASE_URL from database.py:", DATABASE_URL)
print("=" * 50)


from models import create_tables, Role, User, Movie, Cinema, Hall, Session, Ticket

engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True
)

create_tables(engine)

SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

SECRET_KEY = "secret-keyyy" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBearer()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#здесь будут классы
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class UserRegisterRequest(BaseModel):
    phone: str
    name: str
    password: str
    
    @validator('phone')
    def validate_phone(cls, v):
        if not v or len(v) < 10:
            raise ValueError('Телефон должен содержать 11 символов')
        return v

class UserLoginRequest(BaseModel):
    phone: str
    password: str

class UserResponse(BaseModel):
    phone: str
    name: str
    role_id: int

def verify_password(plain_password, hashed_password):
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Хеширование пароля"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создание JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Получает текущего пользователя из JWT токена"""
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone: str = payload.get("sub")
        
        if phone is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный токен",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.phone == phone).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def get_current_admin(current_user: User = Depends(get_current_user)):
    """
    Проверить, что текущий пользователь является администратором
    """
    if current_user.role_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен. Требуются права администратора"
        )
    return current_user

@app.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Регистрация нового пользователя
    """
    existing_user = db.query(User).filter(User.phone == user_data.phone).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким номером телефона уже существует"
        )
    
    hashed_password = get_password_hash(user_data.password)
    
    new_user = User(
        phone=user_data.phone,
        name=user_data.name,
		role_id=2,
        password=hashed_password,
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(
        data={
            "sub": new_user.phone,
            "name": new_user.name,
            "role_id": new_user.role_id
        }
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "phone": new_user.phone,
            "name": new_user.name,
            "role_id": new_user.role_id
        }
    }

@app.post("/auth/login", response_model=TokenResponse)
def login(
    login_data: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Вход в систему
    """
    user = db.query(User).filter(User.phone == login_data.phone).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный номер телефона или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный номер телефона или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={
            "sub": user.phone,
            "name": user.name,
            "role_id": user.role_id
        }
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "phone": user.phone,
            "name": user.name,
			"role_id": user.role_id
        }
    }

@app.get("/auth/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Получить информацию о текущем пользователе
    """
    return {
        "phone": current_user.phone,
        "name": current_user.name,
        "role_id": current_user.role_id
    }

@app.post("/auth/logout")
def logout():
    """
    Выход из системы
    """
    return {"message": "Выход выполнен успешно"}