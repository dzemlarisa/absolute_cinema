from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, CheckConstraint
from sqlalchemy.orm import declarative_base, relationship

from datetime import datetime

Base = declarative_base()

class Role(Base):
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    
    users = relationship('User', back_populates='role', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(String(11), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)
    password = Column(String(255), nullable=False)

    role = relationship('Role', back_populates='users')
    tickets = relationship('Ticket', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', phone='{self.phone}', role_id={self.role_id})>"

class Movie(Base):
    __tablename__ = 'movies'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    year = Column(Integer, nullable=False)
    director = Column(String(100), nullable=False)
    operator = Column(String(100), nullable=True)
    actors = Column(String(500), nullable=True)
    genre = Column(String(50), nullable=False)
    studio = Column(String(100), nullable=True)
    time = Column(String(10), nullable=False)
    price = Column(Integer, nullable=False)
    
    sessions = relationship('Session', back_populates='movie', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Movie(id={self.id}, name='{self.name}', director='{self.director}', genre='{self.genre}')>"

class Cinema(Base):
    __tablename__ = 'cinemas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    address = Column(String(200), nullable=False)

    halls = relationship('Hall', back_populates='cinema', cascade='all, delete-orphan')
    sessions = relationship('Session', back_populates='cinema', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Cinema(id={self.id}, name='{self.name}', address='{self.address}')>"

class Hall(Base):
    __tablename__ = 'halls'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cinema_id = Column(Integer, ForeignKey('cinemas.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(50), nullable=False)
    capacity = Column(Integer, nullable=False)

    cinema = relationship('Cinema', back_populates='halls')
    sessions = relationship('Session', back_populates='hall', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Hall(id={self.id}, name='{self.name}', cinema_id={self.cinema_id}, capacity={self.capacity})>"

class Session(Base):
    __tablename__ = 'sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cinema_id = Column(Integer, ForeignKey('cinemas.id', ondelete='CASCADE'), nullable=False)
    hall_id = Column(Integer, ForeignKey('halls.id', ondelete='CASCADE'), nullable=False)
    movie_id = Column(Integer, ForeignKey('movies.id', ondelete='CASCADE'), nullable=False)
    start_time = Column(String(50), nullable=False)
    end_time = Column(String(50), nullable=False)
    remaining_seats = Column(Integer, nullable=False)
    
    cinema = relationship('Cinema', back_populates='sessions')
    hall = relationship('Hall', back_populates='sessions')
    movie = relationship('Movie', back_populates='sessions')
    tickets = relationship('Ticket', back_populates='session', cascade='all, delete-orphan')
    
    __table_args__ = (
        CheckConstraint('remaining_seats >= 0', name='check_remaining_seats_non_negative'),
    )
    
    def __repr__(self):
        return f"<Session(id={self.id}, movie_id={self.movie_id}, cinema_id={self.cinema_id}, start_time={self.start_time}, remaining_seats={self.remaining_seats})>"

class Ticket(Base):
    __tablename__ = 'tickets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    session_id = Column(Integer, ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)
    ticket_cnt = Column(Integer, nullable=False)
    total = Column(Numeric(10, 2), nullable=False)
    
    user = relationship('User', back_populates='tickets')
    session = relationship('Session', back_populates='tickets')

    __table_args__ = (
        CheckConstraint('ticket_cnt > 0', name='check_ticket_cnt_positive'),
    )
    
    def __repr__(self):
        return f"<Ticket(id={self.id}, user_id={self.user_id}, session_id={self.session_id}, ticket_cnt={self.ticket_cnt}, total={self.total}, status='{self.status}')>"

def create_tables(engine):
    """
    Функция для создания всех таблиц в базе данных
    """
    #Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("Все таблицы успешно созданы (или уже существуют)")

