import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Role, Movie, Cinema, Hall, Session, Ticket
from datetime import datetime, timedelta

# Тестовая база данных SQLite (в памяти)
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    """Создаёт тестовую сессию БД"""
    engine = create_engine(TEST_DATABASE_URL, echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

def test_create_role(db_session):
    """Тест создания роли"""
    role = Role(name="client")
    db_session.add(role)
    db_session.commit()
    
    saved_role = db_session.query(Role).first()
    assert saved_role is not None
    assert saved_role.name == "client"

def test_create_user(db_session):
    """Тест создания пользователя"""
    role = Role(name="client")
    db_session.add(role)
    db_session.commit()
    
    user = User(
        phone="89991234567",
        name="Тестовый Пользователь",
        role_id=role.id,
        password="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    
    saved_user = db_session.query(User).first()
    assert saved_user.phone == "89991234567"
    assert saved_user.name == "Тестовый Пользователь"

def test_create_movie(db_session):
    """Тест создания фильма"""
    movie = Movie(
        name="Тестовый фильм",
        year=2026,
        director="Тестовый режиссёр",
        operator="Оператор",
        actors="Актер",
        genre="фантастика",
        studio="Студия",
        time=120,
        price=350
    )
    db_session.add(movie)
    db_session.commit()
    
    saved_movie = db_session.query(Movie).first()
    assert saved_movie.name == "Тестовый фильм"
    assert saved_movie.price == 350

def test_create_cinema_and_hall(db_session):
    """Тест создания кинотеатра и зала"""
    cinema = Cinema(name="Тест Кинотеатр", address="ул. Тестовая, 1")
    db_session.add(cinema)
    db_session.commit()
    
    hall = Hall(cinema_id=cinema.id, name="Зал 1", capacity=100)
    db_session.add(hall)
    db_session.commit()
    
    saved_cinema = db_session.query(Cinema).first()
    saved_hall = db_session.query(Hall).first()
    
    assert saved_cinema.name == "Тест Кинотеатр"
    assert saved_hall.cinema_id == saved_cinema.id
    assert saved_hall.capacity == 100

def test_create_session(db_session):
    """Тест создания сеанса"""
    cinema = Cinema(name="Кинотеатр", address="ул. Тестовая, 1")
    hall = Hall(cinema_id=1, name="Зал 1", capacity=100)
    movie = Movie(name="Тестовый фильм", year=2026, director="Тестовый режиссёр", operator="Оператор", actors="Актер", genre="фантастика", studio="Студия", time=120, price=350)
    db_session.add_all([cinema, hall, movie])
    db_session.commit()
    
    session = Session(
        cinema_id=cinema.id,
        hall_id=hall.id,
        movie_id=movie.id,
        start_time = datetime(2026, 6, 18, 17, 0)
    )
    db_session.add(session)
    db_session.commit()
    
    saved_session = db_session.query(Session).first()
    assert saved_session.cinema_id == cinema.id
    assert saved_session.remaining_seats == 100