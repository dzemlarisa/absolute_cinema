import jwt
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import text, create_engine, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, validator
from passlib.context import CryptContext
from jwt.exceptions import PyJWTError
import pytz

from database import get_db, engine, DATABASE_URL
from models import create_tables, Base, Role, User, Movie, Cinema, Hall, Session as SessionModel, Ticket

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

class MovieBase(BaseModel):
    name: str
    year: int
    director: str
    operator: Optional[str] = None
    actors: Optional[str] = None
    genre: str
    studio: Optional[str] = None
    time: int
    price: float

class MovieCreate(MovieBase):
    pass

class MovieUpdate(BaseModel):
    name: Optional[str] = None
    year: Optional[int] = None
    director: Optional[str] = None
    operator: Optional[str] = None
    actors: Optional[str] = None
    genre: Optional[str] = None
    studio: Optional[str] = None
    time: Optional[int] = None
    price: Optional[float] = None

class MovieResponse(MovieBase):
    id: int
    class Config:
        from_attributes = True

class CinemaBase(BaseModel):
    name: str
    address: str

class CinemaCreate(CinemaBase):
    pass

class CinemaUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None

class CinemaResponse(CinemaBase):
    id: int
    class Config:
        from_attributes = True

class HallBase(BaseModel):
    name: str
    capacity: int

class HallCreate(HallBase):
    pass

class HallResponse(HallBase):
    id: int
    cinema_id: int
    class Config:
        from_attributes = True

class SessionBase(BaseModel):
    cinema_id: int
    hall_id: int
    movie_id: int
    start_time: str

class SessionCreate(SessionBase):
    pass

class SessionResponse(SessionBase):
    id: int
    start_time: datetime
    end_time: datetime
    remaining_seats: int
    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, session):
        return cls(
            id=session.id,
            start_time=session.start_time.strftime('%Y-%m-%d %H:%M'),
            end_time=session.end_time.strftime('%Y-%m-%d %H:%M')
        )

class TicketBase(BaseModel):
    session_id: int
    ticket_cnt: int

class TicketCreate(TicketBase):
    pass

class TicketResponse(BaseModel):
    id: int
    user_id: int
    session_id: int
    ticket_cnt: int
    total: float
    status: str
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    phone: str
    name: str
    role_id: int
    class Config:
        from_attributes = True

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

@app.get("/users", response_model=List[UserResponse])
async def get_users(

    db: Session = Depends(get_db)
):
    """Возвращает список всех пользователей"""
    users = db.query(User).all()
    return users

#Эндпоинты для фильмов
@app.get("/movies", response_model=List[MovieResponse])
async def get_movies(
    genre: Optional[str] = Query(None, description="Фильтр по жанру"),
    director: Optional[str] = Query(None, description="Фильтр по режиссёру"),
    year: Optional[int] = Query(None, description="Фильтр по году выпуска"),
    db: Session = Depends(get_db)
):
    """Возвращает список всех фильмов с возможностью фильтрации по жанру, режиссёру, году"""
    query = db.query(Movie)
    
    if genre:
        query = query.filter(Movie.genre.ilike(f"%{genre}%"))
    if director:
        query = query.filter(Movie.director.ilike(f"%{director}%"))
    if year:
        query = query.filter(Movie.year == year)
    
    return query.all()

@app.get("/movies/{movie_id}", response_model=MovieResponse)
async def get_movie(
    movie_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Возвращает информацию о фильме по его id"""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    return movie

@app.post("/movies", response_model=MovieResponse)
async def create_movie(
    movie_data: MovieCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Добавляет новый фильм"""
    try:
        existing_movie = db.query(Movie).filter(Movie.name == movie_data.name).first()
        if existing_movie:
            raise HTTPException(status_code=400, detail="Фильм с таким названием уже существует")
        
        new_movie = Movie(**movie_data.model_dump())
        db.add(new_movie)
        db.commit()
        db.refresh(new_movie)
        return new_movie
    except Exception as e:
        print(f"ОШИБКА: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/movies/{movie_id}", response_model=MovieResponse)
async def update_movie(
    movie_id: int,
    movie_data: MovieUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    try:
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if not movie:
            raise HTTPException(status_code=404, detail="Фильм не найден")
        
        update_data = movie_data.model_dump(exclude_unset=True)
        print(f"Обновляем поля: {update_data}")
        
        for key, value in update_data.items():
            if value is not None:
                setattr(movie, key, value)
        
        db.commit()
        db.refresh(movie)
        return movie
        
    except Exception as e:
        db.rollback()
        print(f"Ошибка: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/movies/{movie_id}")
async def delete_movie(
    movie_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Удаляет фильм по id"""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    
    active_sessions = db.query(SessionModel).filter(SessionModel.movie_id == movie_id).first()
    if active_sessions:
        raise HTTPException(status_code=400, detail="Невозможно удалить фильм с активными сеансами")
    
    db.delete(movie)
    db.commit()
    return {"message": "Фильм успешно удалён"}

#-------------------------не работает---------------------
@app.get("/movies/genres")
async def get_genres(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Возвращает список жанров"""
    genres = db.query(Movie.genre).distinct().all()
    return [genre[0] for genre in genres if genre[0]]

@app.get("/movies/directors")
async def get_directors(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Возвращает список режиссёров"""
    directors = db.query(Movie.director).distinct().all()
    return [director[0] for director in directors if director[0]]
#--------------------------------------------------------

#эндпоинты для кинотеатров
@app.get("/cinemas", response_model=List[CinemaResponse])
async def get_cinemas(
    db: Session = Depends(get_db)
):
    """Возвращает список кинотеатров"""
    return db.query(Cinema).all()

@app.get("/cinemas/{cinema_id}", response_model=CinemaResponse)
async def get_cinema(
    cinema_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Возвращает информацию о кинотеатре по его id"""
    cinema = db.query(Cinema).filter(Cinema.id == cinema_id).first()
    if not cinema:
        raise HTTPException(status_code=404, detail="Кинотеатр не найден")
    return cinema

@app.post("/cinemas", response_model=CinemaResponse)
async def create_cinema(
    cinema_data: CinemaCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Добавляет новый кинотеатр"""
    existing_cinema = db.query(Cinema).filter(Cinema.name == cinema_data.name).first()
    if existing_cinema:
        raise HTTPException(status_code=400, detail="Кинотеатр с таким названием уже существует")
    
    new_cinema = Cinema(**cinema_data.model_dump())
    db.add(new_cinema)
    db.commit()
    db.refresh(new_cinema)
    return new_cinema

@app.put("/cinemas/{cinema_id}", response_model=CinemaResponse)
async def update_cinema(
    cinema_id: int,
    cinema_data: CinemaUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Обновляет информацию о кинотеатре"""
    cinema = db.query(Cinema).filter(Cinema.id == cinema_id).first()
    if not cinema:
        raise HTTPException(status_code=404, detail="Кинотеатр не найден")
    
    for key, value in cinema_data.model_dump(exclude_unset=True).items():
        setattr(cinema, key, value)
    
    db.commit()
    db.refresh(cinema)
    return cinema

@app.delete("/cinemas/{cinema_id}")
async def delete_cinema(
    cinema_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Удаляет кинотеатр по id"""
    cinema = db.query(Cinema).filter(Cinema.id == cinema_id).first()
    if not cinema:
        raise HTTPException(status_code=404, detail="Кинотеатр не найден")

    active_sessions = db.query(SessionModel).filter(SessionModel.cinema_id == cinema_id).first()
    if active_sessions:
        raise HTTPException(status_code=400, detail="Невозможно удалить кинотеатр с активными сеансами")
    
    db.delete(cinema)
    db.commit()
    return {"message": "Кинотеатр успешно удалён"}

#эндпоинты для залов
@app.get("/cinemas/{cinema_id}/halls", response_model=List[HallResponse])
async def get_cinema_halls(
    cinema_id: int,
    db: Session = Depends(get_db)
):
    """Возвращает список залов конкретного кинотеатра"""
    cinema = db.query(Cinema).filter(Cinema.id == cinema_id).first()
    if not cinema:
        raise HTTPException(status_code=404, detail="Кинотеатр не найден")
    
    return db.query(Hall).filter(Hall.cinema_id == cinema_id).all()

@app.get("/halls/{hall_id}", response_model=HallResponse)
async def get_hall(
    hall_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Возвращает информацию о зале по его id"""
    hall = db.query(Hall).filter(Hall.id == hall_id).first()
    if not hall:
        raise HTTPException(status_code=404, detail="Зал не найден")
    return hall

@app.post("/cinemas/{cinema_id}/halls", response_model=HallResponse)
async def create_hall(
    cinema_id: int,
    hall_data: HallCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Добавляет новый зал в кинотеатр"""
    cinema = db.query(Cinema).filter(Cinema.id == cinema_id).first()
    if not cinema:
        raise HTTPException(status_code=404, detail="Кинотеатр не найден")
    
    new_hall = Hall(cinema_id=cinema_id, **hall_data.dict())
    db.add(new_hall)
    db.commit()
    db.refresh(new_hall)
    return new_hall

@app.delete("/halls/{hall_id}")
async def delete_hall(
    hall_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Удаляет зал по id"""
    hall = db.query(Hall).filter(Hall.id == hall_id).first()
    if not hall:
        raise HTTPException(status_code=404, detail="Зал не найден")
    
    active_sessions = db.query(SessionModel).filter(SessionModel.hall_id == hall_id).first()
    if active_sessions:
        raise HTTPException(status_code=400, detail="Невозможно удалить зал с активными сеансами")
    
    db.delete(hall)
    db.commit()
    return {"message": "Зал успешно удалён"}

#эндпоинты для сеансов
@app.get("/sessions", response_model=List[SessionResponse])
async def get_sessions(
    movie_id: Optional[int] = Query(None, description="Фильтр по ID фильма"),
    cinema_id: Optional[int] = Query(None, description="Фильтр по ID кинотеатра"),
    date: Optional[str] = Query(None, description="Фильтр по дате (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Возвращает список сеансов с возможностью фильтрации"""
    query = db.query(SessionModel)
    
    if movie_id:
        query = query.filter(SessionModel.movie_id == movie_id)
    if cinema_id:
        query = query.filter(SessionModel.cinema_id == cinema_id)
    if date:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
        query = query.filter(
            and_(
                SessionModel.start_time >= target_date,
                SessionModel.start_time < target_date.replace(day=target_date.day + 1)
            )
        )
    
    return query.all()

@app.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Возвращает информацию о сеансе по его id"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Сеанс не найден")
    return session

@app.post("/sessions", response_model=SessionResponse)
async def create_session(
    session_data: SessionCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Добавляет новый сеанс"""
    #moscow_tz = pytz.timezone('Europe/Moscow')
    #start_time = moscow_tz.localize(naive_start_time)

    start_time_str = session_data.start_time
    start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M')
    
    movie = db.query(Movie).filter(Movie.id == session_data.movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    
    cinema = db.query(Cinema).filter(Cinema.id == session_data.cinema_id).first()
    if not cinema:
        raise HTTPException(status_code=404, detail="Кинотеатр не найден")
    
    hall = db.query(Hall).filter(Hall.id == session_data.hall_id).first()
    if not hall:
        raise HTTPException(status_code=404, detail="Зал не найден")
    
    if hall.cinema_id != session_data.cinema_id:
        raise HTTPException(status_code=400, detail="Зал не принадлежит указанному кинотеатру")
    
    if start_time.minute % 5 != 0:
        raise HTTPException(400, "Время должно быть кратно 5 минутам")    
    
    movie_duration = int(movie.time)
    end_time = start_time + timedelta(minutes=movie_duration)
    
    overlapping = db.query(SessionModel).filter(
        and_(
            SessionModel.hall_id == session_data.hall_id,
            SessionModel.start_time < end_time,
            SessionModel.end_time > start_time
        )
    ).first()
    
    if overlapping:
        raise HTTPException(
            status_code=400, 
            detail="Время сеанса пересекается с существующим сеансом в этом зале"
        )
    
    new_session = SessionModel(
        movie_id=session_data.movie_id,
        cinema_id=session_data.cinema_id,
        hall_id=session_data.hall_id,
        start_time=start_time,
        end_time=end_time,
        remaining_seats=hall.capacity
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@app.delete("/sessions/{session_id}")
async def delete_session(
    session_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Удаляет сеанс по id"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Сеанс не найден")
    
    tickets = db.query(Ticket).filter(Ticket.session_id == session_id).first()
    if tickets:
        raise HTTPException(status_code=400, detail="Невозможно удалить сеанс с проданными билетами")
    
    db.delete(session)
    db.commit()
    return {"message": "Сеанс успешно удалён"}

@app.get("/movies/{movie_id}/sessions", response_model=List[SessionResponse])
async def get_movie_sessions(
    movie_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Возвращает список сеансов для конкретного фильма"""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    
    return db.query(SessionModel).filter(SessionModel.movie_id == movie_id).all()

@app.get("/cinemas/{cinema_id}/sessions", response_model=List[SessionResponse])
async def get_cinema_sessions(
    cinema_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Возвращает список сеансов для конкретного кинотеатра"""
    cinema = db.query(Cinema).filter(Cinema.id == cinema_id).first()
    if not cinema:
        raise HTTPException(status_code=404, detail="Кинотеатр не найден")
    
    return db.query(SessionModel).filter(SessionModel.cinema_id == cinema_id).all()