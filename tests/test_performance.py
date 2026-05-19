import time
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Переопределяем DATABASE_URL для тестов ДО импорта main
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

from main import app

client = TestClient(app)

def test_response_time_get_movies():
    """Тест: время отклика GET /movies не должно превышать 200 мс"""
    start_time = time.time()
    response = client.get("/movies")
    elapsed_ms = (time.time() - start_time) * 1000
    
    assert response.status_code == 200
    assert elapsed_ms < 200, f"Время отклика {elapsed_ms:.2f} мс превышает 200 мс"


def test_response_time_get_cinemas():
    """Тест: время отклика GET /cinemas не должно превышать 200 мс"""
    start_time = time.time()
    response = client.get("/cinemas")
    elapsed_ms = (time.time() - start_time) * 1000
    
    assert response.status_code == 200
    assert elapsed_ms < 200, f"Время отклика {elapsed_ms:.2f} мс превышает 200 мс"


def test_response_time_create_movie():
    """Тест: время отклика POST /movies не должно превышать 300 мс"""
    movie_data = {
        "name": "Тест скорости",
        "director": "Быстрый режиссёр",
        "genre": "тест",
        "time": "90",
        "price": 300
    }
    start_time = time.time()
    response = client.post("/movies", json=movie_data)
    elapsed_ms = (time.time() - start_time) * 1000
    
    assert response.status_code == 200
    assert elapsed_ms < 300, f"Время отклика {elapsed_ms:.2f} мс превышает 300 мс"