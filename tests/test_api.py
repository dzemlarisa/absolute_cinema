import pytest
from fastapi.testclient import TestClient
from main import app
from database import get_db
from models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer demo"}

def test_get_movies_empty(client, auth_headers):
    response = client.get("/movies", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []

def test_create_movie(client, auth_headers):
    movie_data = {
        "name": "Тестовый фильм",
        "year": 2026,
        "director": "Тестовый режиссёр",
        "operator": "Тестовый оператор",
        "actors": "Актёр 1, Актёр 2",
        "genre": "фантастика",
        "studio": "Тест Студия",
        "time": 120,
        "price": 350
    }
    response = client.post("/movies", json=movie_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Тестовый фильм"
    assert data["price"] == 350
    assert "id" in data

def test_get_movies_after_create(client, auth_headers):
    movie_data = {
        "name": "Тестовый фильм",
        "year": 2026,
        "director": "Тестовый режиссёр",
        "operator": "Тестовый оператор",
        "actors": "Актёр 1, Актёр 2",
        "genre": "фантастика",
        "studio": "Тест Студия",
        "time": 120,
        "price": 350
    }
    client.post("/movies", json=movie_data, headers=auth_headers)

    response = client.get("/movies", headers=auth_headers)
    assert response.status_code == 200
    movies = response.json()
    assert len(movies) >= 1
    assert movies[0]["name"] == "Фильм для теста"

def test_get_movie_by_id(client, auth_headers):
    movie_data = {
        "name": "Тестовый фильм",
        "year": 2026,
        "director": "Тестовый режиссёр",
        "operator": "Тестовый оператор",
        "actors": "Актёр 1, Актёр 2",
        "genre": "фантастика",
        "studio": "Тест Студия",
        "time": 120,
        "price": 350
    }
    create_response = client.post("/movies", json=movie_data, headers=auth_headers)
    movie_id = create_response.json()["id"]

    response = client.get(f"/movies/{movie_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Фильм по ID"

def test_get_movie_not_found(client, auth_headers):
    response = client.get("/movies/99999", headers=auth_headers)
    assert response.status_code == 404
    assert "не найден" in response.json()["detail"]

def test_update_movie(client, auth_headers):
    movie_data = {
        "name": "Тестовый фильм",
        "year": 2026,
        "director": "Тестовый режиссёр",
        "operator": "Тестовый оператор",
        "actors": "Актёр 1, Актёр 2",
        "genre": "фантастика",
        "studio": "Тест Студия",
        "time": 120,
        "price": 350
    }

    create_response = client.post("/movies", json=movie_data, headers=auth_headers)
    movie_id = create_response.json()["id"]

    update_data = {"name": "Новое название"}
    response = client.put(f"/movies/{movie_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Новое название"

def test_delete_movie(client, auth_headers):
    movie_data = {
        "name": "Тестовый фильм",
        "year": 2026,
        "director": "Тестовый режиссёр",
        "operator": "Тестовый оператор",
        "actors": "Актёр 1, Актёр 2",
        "genre": "фантастика",
        "studio": "Тест Студия",
        "time": 120,
        "price": 350
    }
    create_response = client.post("/movies", json=movie_data, headers=auth_headers)
    movie_id = create_response.json()["id"]

    response = client.delete(f"/movies/{movie_id}", headers=auth_headers)
    assert response.status_code == 200
    assert "успешно удалён" in response.json()["message"]

    get_response = client.get(f"/movies/{movie_id}", headers=auth_headers)
    assert get_response.status_code == 404

def test_get_cinemas(client, auth_headers):
    response = client.get("/cinemas", headers=auth_headers)
    assert response.status_code == 200

def test_create_cinema(client, auth_headers):
    cinema_data = {
        "name": "Тестовый Кинотеатр",
        "address": "ул. Тестовая, 10"
    }
    response = client.post("/cinemas", json=cinema_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Тестовый Кинотеатр"

def test_get_genres(client, auth_headers):
    movies = [
        {"name": "Фантастика 1", "director": "Реж 1", "genre": "фантастика", "time": 90, "price": 300},
        {"name": "Драма 1", "director": "Реж 2", "genre": "драма", "time": 100, "price": 320},
        {"name": "Комедия 1", "director": "Реж 3", "genre": "комедия", "time": 95, "price": 280}
    ]
    for movie in movies:
        client.post("/movies", json=movie, headers=auth_headers)
    
    response = client.get("/movies/genres", headers=auth_headers)
    assert response.status_code == 200
    genres = response.json()
    assert "фантастика" in genres
    assert "драма" in genres