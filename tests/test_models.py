import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Role, Movie, Cinema, Hall, Session, Ticket
from datetime import datetime, timedelta

TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    engine = create_engine(TEST_DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

def test_create_role(db_session):
    role = Role(name="client")
    db_session.add(role)
    db_session.commit()
    
    saved_role = db_session.query(Role).first()
    assert saved_role is not None
    assert saved_role.name == "client"

def test_create_user(db_session):
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
    cinema = Cinema(name="Тест Кинотеатр", address="ул. Тестовая, 1")
    db_session.add(cinema)
    db_session.commit()  # Коммитим, чтобы cinema получил id
    
    hall = Hall(cinema_id=cinema.id, name="Зал 1", capacity=100)
    db_session.add(hall)
    db_session.commit()
    
    saved_cinema = db_session.query(Cinema).first()
    saved_hall = db_session.query(Hall).first()
    
    assert saved_cinema.name == "Тест Кинотеатр"
    assert saved_hall.cinema_id == saved_cinema.id
    assert saved_hall.capacity == 100

def test_create_session(db_session):
    # Создаём все необходимые объекты
    cinema = Cinema(name="Кинотеатр", address="ул. Тестовая, 1")
    db_session.add(cinema)
    db_session.flush()  # Получаем ID без коммита
    
    hall = Hall(cinema_id=cinema.id, name="Зал 1", capacity=100)
    db_session.add(hall)
    db_session.flush()
    
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
    db_session.flush()
    
    start_time = datetime(2026, 6, 18, 17, 0)
    end_time = start_time + timedelta(minutes=movie.time)
    
    session = Session(
        cinema_id=cinema.id,
        hall_id=hall.id,
        movie_id=movie.id,
        start_time=start_time,
        end_time=end_time,
        remaining_seats=hall.capacity
    )
    db_session.add(session)
    db_session.commit()  # Финальный коммит
    
    saved_session = db_session.query(Session).first()
    assert saved_session is not None
    assert saved_session.cinema_id == cinema.id
    assert saved_session.hall_id == hall.id
    assert saved_session.movie_id == movie.id
    assert saved_session.remaining_seats == 100
    assert saved_session.start_time == start_time
    assert saved_session.end_time == end_time

def test_create_ticket(db_session):
    # Создаём все необходимые объекты
    role = Role(name="Пользователь")
    db_session.add(role)
    db_session.flush()
    
    user = User(
        phone="89991234567",
        name="Тестовый Пользователь",
        role_id=role.id,
        password="hashed_password"
    )
    db_session.add(user)
    db_session.flush()
    
    cinema = Cinema(name="Кинотеатр", address="ул. Тестовая, 1")
    db_session.add(cinema)
    db_session.flush()
    
    hall = Hall(cinema_id=cinema.id, name="Зал 1", capacity=100)
    db_session.add(hall)
    db_session.flush()
    
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
    db_session.flush()
    
    start_time = datetime(2026, 6, 18, 17, 0)
    end_time = start_time + timedelta(minutes=movie.time)
    
    session = Session(
        cinema_id=cinema.id,
        hall_id=hall.id,
        movie_id=movie.id,
        start_time=start_time,
        end_time=end_time,
        remaining_seats=hall.capacity
    )
    db_session.add(session)
    db_session.flush()
    
    ticket_count = 2
    ticket = Ticket(
        user_id=user.id,
        session_id=session.id,
        ticket_cnt=ticket_count,
        total=movie.price*ticket_count
    )
    db_session.add(ticket)
    db_session.commit()
    
    saved_ticket = db_session.query(Ticket).first()
    assert saved_ticket is not None
    assert saved_ticket.user_id == user.id
    assert saved_ticket.session_id == session.id
    assert saved_ticket.total == movie.price*ticket_count