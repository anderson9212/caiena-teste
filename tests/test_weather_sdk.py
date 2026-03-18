"""Tests for Weather Comment API components."""

import os
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch
import pytest
from requests.exceptions import ConnectTimeout, HTTPError, Timeout
from exceptions import CityNotFoundError, WeatherAPIException
from schemas import CurrentWeather, Forecast, ForecastDay, WeatherComment
from weather_sdk import OpenWeatherMapSDK


@pytest.fixture
def api_key():
    return "test_api_key_123"


@pytest.fixture
def weather_sdk(api_key, monkeypatch):
    monkeypatch.setattr("config.Config.OPENWEATHER_API_KEY", api_key)
    return OpenWeatherMapSDK()


@pytest.fixture
def mock_weather_response():
    return {
        "main": {"temp": 25.5},
        "weather": [{"description": "Parcialmente Nublado"}],
        "name": "São Paulo",
    }


@pytest.fixture
def mock_forecast_response():
    return {
        "list": [
            {"dt": 1615987200, "main": {"temp": 22.0}},
            {"dt": 1615987200, "main": {"temp": 23.0}},
            {"dt": 1616073600, "main": {"temp": 24.0}},
            {"dt": 1616160000, "main": {"temp": 21.5}},
            {"dt": 1616246400, "main": {"temp": 24.0}},
            {"dt": 1616332800, "main": {"temp": 25.0}},
        ]
    }



class TestOpenWeatherMapSDKInitialization:
    def test_initialization_with_api_key(self, api_key, monkeypatch):
        monkeypatch.setattr("config.Config.OPENWEATHER_API_KEY", api_key)
        sdk = OpenWeatherMapSDK()
        assert sdk.api_key == api_key
        assert sdk.base_url == "http://api.openweathermap.org/data/2.5"

    def test_initialization_with_env_variable(self, monkeypatch):
        test_key = "env_test_key"
        monkeypatch.setattr("config.Config.OPENWEATHER_API_KEY", test_key)
        sdk = OpenWeatherMapSDK()
        assert sdk.api_key == test_key

    def test_initialization_without_api_key_raises_error(self, monkeypatch):
        monkeypatch.setattr("config.Config.OPENWEATHER_API_KEY", None)
        with pytest.raises(ValueError, match="Chave da API do OpenWeatherMap é obrigatória"):
            OpenWeatherMapSDK()

    def test_initialization_sets_timeout(self, weather_sdk):
        assert hasattr(weather_sdk, "timeout")
        assert weather_sdk.timeout > 0


class TestGetCurrentWeather:
    @patch("weather_sdk.requests.get")
    def test_get_current_weather_success(self, mock_get, weather_sdk, mock_weather_response):
        mock_response = Mock()
        mock_response.json.return_value = mock_weather_response
        mock_get.return_value = mock_response

        result = weather_sdk.get_current_weather("São Paulo")

        assert isinstance(result, CurrentWeather)
        assert result.temperature == 25.5
        assert result.description == "Parcialmente Nublado"
        assert result.city == "São Paulo"
        assert isinstance(result.timestamp, datetime)
        mock_get.assert_called_once()

    @patch("weather_sdk.requests.get")
    def test_get_current_weather_city_not_found(self, mock_get, weather_sdk):
        mock_response = Mock()
        http_error = HTTPError()
        http_error.response = Mock(status_code=404)
        mock_response.raise_for_status.side_effect = http_error
        mock_get.return_value = mock_response

        with pytest.raises(CityNotFoundError) as exc_info:
            weather_sdk.get_current_weather("NonExistentCity")

        assert "NonExistentCity" in str(exc_info.value)

    @patch("weather_sdk.requests.get")
    def test_get_current_weather_http_error(self, mock_get, weather_sdk):
        mock_response = Mock()
        http_error = HTTPError()
        http_error.response = Mock(status_code=500)
        mock_response.raise_for_status.side_effect = http_error
        mock_get.return_value = mock_response

        with pytest.raises(WeatherAPIException) as exc_info:
            weather_sdk.get_current_weather("São Paulo")

        assert exc_info.value.error_code == "WEATHER_API_ERROR"

    @patch("weather_sdk.requests.get")
    def test_get_current_weather_connection_error(self, mock_get, weather_sdk):
        mock_get.side_effect = ConnectTimeout("Connection failed")

        with pytest.raises(WeatherAPIException):
            weather_sdk.get_current_weather("São Paulo")

    @patch("weather_sdk.requests.get")
    def test_get_current_weather_invalid_data(self, mock_get, weather_sdk):
        mock_response = Mock()
        mock_response.json.return_value = {"invalid": "data"}
        mock_get.return_value = mock_response

        with pytest.raises(WeatherAPIException):
            weather_sdk.get_current_weather("São Paulo")


class TestGetForecast:
    @patch("weather_sdk.requests.get")
    def test_get_forecast_success(self, mock_get, weather_sdk, mock_forecast_response):
        mock_response = Mock()
        mock_response.json.return_value = mock_forecast_response
        mock_get.return_value = mock_response

        result = weather_sdk.get_forecast("São Paulo", days=5)

        assert isinstance(result, Forecast)
        assert result.city == "São Paulo"
        assert len(result.forecast_days) > 0
        assert all(isinstance(f, ForecastDay) for f in result.forecast_days)
        mock_get.assert_called_once()

    @patch("weather_sdk.requests.get")
    def test_get_forecast_with_custom_days(self, mock_get, weather_sdk, mock_forecast_response):
        mock_response = Mock()
        mock_response.json.return_value = mock_forecast_response
        mock_get.return_value = mock_response

        result = weather_sdk.get_forecast("São Paulo", days=3)

        assert len(result.forecast_days) <= 3

    @patch("weather_sdk.requests.get")
    def test_get_forecast_city_not_found(self, mock_get, weather_sdk):
        mock_response = Mock()
        http_error = HTTPError()
        http_error.response = Mock(status_code=404)
        mock_response.raise_for_status.side_effect = http_error
        mock_get.return_value = mock_response

        with pytest.raises(CityNotFoundError):
            weather_sdk.get_forecast("NonExistentCity")

    @patch("weather_sdk.requests.get")
    def test_get_forecast_temperature_averaging(self, mock_get, weather_sdk):
        mock_response = Mock()
        mock_response.json.return_value = {
            "list": [
                {"dt": 1615987200, "main": {"temp": 20.0}},
                {"dt": 1615987200, "main": {"temp": 24.0}},
                {"dt": 1616073600, "main": {"temp": 22.0}},
            ]
        }
        mock_get.return_value = mock_response

        result = weather_sdk.get_forecast("São Paulo")

        assert result.forecast_days[0].avg_temp == 22.0


class TestCurrentWeatherSchema:
    def test_current_weather_creation(self):
        weather = CurrentWeather(
            temperature=25.5,
            description="Parcialmente Nublado",
            city="São Paulo",
            timestamp=datetime.now(),
        )
        assert weather.temperature == 25.5
        assert weather.description == "Parcialmente Nublado"
        assert weather.city == "São Paulo"

    def test_current_weather_invalid_temperature(self):
        with pytest.raises(ValueError):
            CurrentWeather(
                temperature="invalid",
                description="Parcialmente Nublado",
                city="São Paulo",
                timestamp=datetime.now(),
            )

    def test_current_weather_invalid_description(self):
        with pytest.raises(ValueError):
            CurrentWeather(
                temperature=25.5,
                description=123,
                city="São Paulo",
                timestamp=datetime.now(),
            )


class TestForecastSchema:
    def test_forecast_creation(self):
        forecast_days = [
            ForecastDay(date="12/03", avg_temp=22.5),
            ForecastDay(date="13/03", avg_temp=23.0),
        ]
        forecast = Forecast(city="São Paulo", forecast_days=forecast_days)
        assert forecast.city == "São Paulo"
        assert len(forecast.forecast_days) == 2

    def test_forecast_empty_days_raises_error(self):
        with pytest.raises(ValueError):
            Forecast(city="São Paulo", forecast_days=[])

    def test_forecast_day_creation(self):
        day = ForecastDay(date="12/03", avg_temp=22.5)
        assert day.date == "12/03"
        assert day.avg_temp == 22.5


class TestWeatherCommentSchema:
    def test_weather_comment_creation(self):
        current_weather = CurrentWeather(
            temperature=32.0,
            description="nublado",
            city="São Paulo",
            timestamp=datetime.now(),
        )
        forecast_days = [
            ForecastDay(date="13/03", avg_temp=28.5),
            ForecastDay(date="14/03", avg_temp=25.0),
        ]
        forecast = Forecast(city="São Paulo", forecast_days=forecast_days)

        comment = WeatherComment(
            city="São Paulo",
            current_weather=current_weather,
            forecast=forecast,
        )

        assert comment.city == "São Paulo"
        assert comment.current_weather == current_weather
        assert comment.forecast == forecast

    def test_weather_comment_formatting(self):
        current_weather = CurrentWeather(
            temperature=32.5,
            description="nublado",
            city="São Paulo",
            timestamp=datetime.now(),
        )
        forecast_days = [
            ForecastDay(date="13/03", avg_temp=28.5),
            ForecastDay(date="14/03", avg_temp=25.0),
        ]
        forecast = Forecast(city="São Paulo", forecast_days=forecast_days)

        comment = WeatherComment(
            city="São Paulo",
            current_weather=current_weather,
            forecast=forecast,
        )

        formatted = comment.format_comment()

        assert "32°C" in formatted
        assert "nublado" in formatted
        assert "São Paulo" in formatted
        assert "Média para os próximos dias" in formatted
        assert "28°C em 13/03" in formatted
        assert "25°C em 14/03" in formatted

    def test_weather_comment_formatting_with_single_forecast_day(self):
        current_weather = CurrentWeather(
            temperature=25.0,
            description="cloudy",
            city="São Paulo",
            timestamp=datetime.now(),
        )
        forecast_days = [ForecastDay(date="13/03", avg_temp=23.0)]
        forecast = Forecast(city="São Paulo", forecast_days=forecast_days)

        comment = WeatherComment(
            city="São Paulo",
            current_weather=current_weather,
            forecast=forecast,
        )

        formatted = comment.format_comment()
        assert "23°C em 13/03" in formatted
