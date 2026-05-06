from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import create_tables, Role, User, Movie, Cinema, Hall, Session, Ticket

DATABASE_URL = 'postgresql://cinema_user:12345@localhost:5432/cinema'

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

