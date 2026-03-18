from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch
from exceptions import WeatherCommentAPIException

client = TestClient(app)


def test_health_check(clear_env_keys):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "message": "API de Comentário de Clima está funcionando"
    }


def test_health_check_error_method(clear_env_keys):
    response = client.post("/")
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}


def test_create_weather_comment_error(clear_env_keys):
    with patch("main.weather_service.create_weather_gist") as mock_create:
        mock_create.side_effect = WeatherCommentAPIException(
            "Cidade não encontrada", error_code="NOT_FOUND", status_code=404
        )
        response = client.post("/weather-comment/Asdf")
        assert response.status_code == 404
        assert response.json() == {"detail": "Cidade não encontrada"}


def test_create_weather_comment_success(clear_env_keys):
    with patch("main.weather_service.create_weather_gist") as mock_create:
        mock_create.return_value = {
            "id": "mock_gist_id_123",
            "url": "https://gist.github.com/mock_gist_id_123",
            "comment": "Previsão do tempo mockada",
            "created_at": "2023-10-01T12:00:00Z"
        }
        response = client.post("/weather-comment/Campinas")
        
        assert response.status_code == 200
        data = response.json()
        assert data["gist_id"] == "mock_gist_id_123"
        assert data["gist_url"] == "https://gist.github.com/mock_gist_id_123"
        assert data["city"] == "Campinas"
        assert data["comment"] == "Previsão do tempo mockada"
