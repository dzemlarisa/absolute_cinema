from sqlalchemy import Column, Integer, String, Text
from passlib.context import CryptContext
from sqlalchemy_utils import database_exists, create_database

from database import engine, SessionLocal
from models import Base, User, Role

INIT_ROLES = [
    {"name": "Админ"},
    {"name": "Пользователь"},
]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

INIT_USERS = [
    {"phone": "89998887766", "name": "Лариса", "role_id": 1, "password": "123"},
]

def init_database():
    if not database_exists(engine.url):
        create_database(engine.url)
        print(f"Создана база данных: {engine.url.database}")
    
    Base.metadata.create_all(bind=engine)
    print("Таблицы созданы")
    db = SessionLocal()
    try:
        role_count = db.query(Role).count()
        if role_count == 0:
            roles = [Role(**role_data) for role_data in INIT_ROLES]
            db.add_all(roles)
            db.commit()
            print(f"Добавлено ролей: {len(INIT_ROLES)}")

        user_count = db.query(User).count()
        if user_count == 0:
            users = []
            for user_data in INIT_USERS:
                user_dict = user_data.copy()
                user_dict["password"] = pwd_context.hash(user_data["password"])
                users.append(User(**user_dict))

            db.add_all(users)
            db.commit()
            print(f"Добавлено пользователей: {len(INIT_USERS)}") 
            
    except Exception as e:
        print(f"Ошибка: {e}")
        db.rollback()
    finally:
        db.close()    

    return engine
    
def main():
    engine = init_database()

if __name__ == "__main__":
    main()