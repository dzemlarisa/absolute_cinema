import time

def test_response_time_get_movies(test_client):
    start_time = time.time()
    response = test_client.get("/auth/register")
    elapsed_ms = (time.time() - start_time) * 1000
    
    print(f"GET запрос: {response.status_code} за {elapsed_ms:.2f} мс")
    assert elapsed_ms < 200, f"Время отклика {elapsed_ms:.2f} мс превышает 200 мс"

def test_response_time_create_movie(test_client):
    movie_data = {
        "name": "Тест скорости",
        "director": "Быстрый режиссёр",
        "genre": "тест",
        "time": 90,
        "price": 300,
        "year": 2026
    }
    
    start_time = time.time()
    response = test_client.post("/movies", json=movie_data)
    elapsed_ms = (time.time() - start_time) * 1000
    
    print(f"POST /movies: {response.status_code} за {elapsed_ms:.2f} мс")
    assert elapsed_ms < 300, f"Время отклика {elapsed_ms:.2f} мс превышает 300 мс"

def test_response_time_create_cinema(test_client):
    cinema_data = {
        "name": "Тестовый кинотеатр",
        "address": "Тестовый адрес"
    }
    
    start_time = time.time()
    response = test_client.post("/cinemas", json=cinema_data)
    elapsed_ms = (time.time() - start_time) * 1000
    
    print(f"POST /cinemas: {response.status_code} за {elapsed_ms:.2f} мс")
    assert elapsed_ms < 300, f"Время отклика {elapsed_ms:.2f} мс превышает 300 мс"