import os
import sys

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['TESTING'] = 'true'

backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'app')
sys.path.insert(0, backend_path)

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URL = 'sqlite:///:memory:'
connect_args = {"check_same_thread": False}
engine = create_engine(TEST_DATABASE_URL, connect_args=connect_args, echo=False)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

import database
database.engine = engine
database.SessionLocal = TestingSessionLocal
database.DATABASE_URL = TEST_DATABASE_URL

from database import Base
from models import User, Role, Movie, Cinema, Hall, Session as SessionModel, Ticket

Base.metadata.create_all(bind=engine)

with TestingSessionLocal() as session:
    session.add(Role(id=1, name="admin"))
    session.add(Role(id=2, name="client"))
    session.commit()

from main import app
from database import get_db
from fastapi.testclient import TestClient

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    yield

@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client