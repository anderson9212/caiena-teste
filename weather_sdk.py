import logging
from datetime import datetime
from typing import Dict, List
import requests
from pydantic import ValidationError
from requests.exceptions import RequestException
from config import Config
from exceptions import CityNotFoundError, WeatherAPIException
from schemas import CurrentWeather, Forecast, ForecastDay

logger = logging.getLogger(__name__)


class OpenWeatherMapSDK:
    def __init__(self) -> None:
        self.api_key = Config.OPENWEATHER_API_KEY
        if not self.api_key:
            logger.error("Chave da api do OpenWeatherMap é obrigatória")
            raise ValueError("Chave da API do OpenWeatherMap é obrigatória")

        self.base_url = Config.OPENWEATHER_BASE_URL
        self.timeout = 10
        logger.debug("SDK OpenWeatherMap inicializado com sucesso")

    def get_current_weather(self, city: str) -> CurrentWeather:
        logger.info(f"Buscando clima atual para cidade: {city}")

        try:
            url = f"{self.base_url}/weather"
            params = {"q": city, "appid": self.api_key, "units": "metric", "lang": "pt_br"}

            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            logger.debug(f"Dados de clima recebidos para {city}: {data}")

            return CurrentWeather(
                temperature=float(data["main"]["temp"]),
                description=data["weather"][0]["description"],
                city=data["name"],
                timestamp=datetime.now(),
            )

        except requests.exceptions.HTTPError as error:
            if error.response.status_code == 404:
                logger.warning(f"Cidade não encontrada: {city}")
                raise CityNotFoundError(city)
            logger.error(f"Erro HTTP ao buscar clima: {error}")
            raise WeatherAPIException(f"Erro HTTP: {error.response.status_code}", error)

        except RequestException as error:
            logger.error(f"Erro de requisição ao buscar clima: {error}")
            raise WeatherAPIException(f"Erro de requisição: {str(error)}", error)

        except ValidationError as error:
            logger.error(f"Erro de validação nos dados de clima: {error}")
            raise WeatherAPIException(f"Dados inválidos da API: {str(error)}", error)

        except (KeyError, ValueError) as error:
            logger.error(f"Formato de dados inválido da API: {error}")
            raise WeatherAPIException(f"Formato de dados inválido: {str(error)}", error)

    def get_forecast(self, city: str, days: int = 5) -> Forecast:
        logger.info(f"Buscando previsão de {days} dias para a cidade: {city}")

        try:
            url = f"{self.base_url}/forecast"
            params = {"q": city, "appid": self.api_key, "units": "metric", "lang": "pt_br"}

            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            logger.debug(f"Dados de previsão recebidos para {city}: {len(data['list'])} itens")

            today_str = datetime.now().strftime("%d/%m")
            daily_temps: Dict[str, List[float]] = {}
            for item in data["list"]:
                date = datetime.fromtimestamp(item["dt"]).strftime("%d/%m")
                
                if date == today_str:
                    continue
                
                temp = float(item["main"]["temp"])

                if date not in daily_temps:
                    daily_temps[date] = []
                daily_temps[date].append(temp)

            forecast_days = []
            for date, temps in list(daily_temps.items())[:days]:
                avg_temp = sum(temps) / len(temps)
                forecast_days.append(
                    ForecastDay(date=date, avg_temp=round(avg_temp, 1))
                )

            logger.debug(f"Processados {len(forecast_days)} dias de previsão")
            return Forecast(city=city, forecast_days=forecast_days)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Cidade não encontrada: {city}")
                raise CityNotFoundError(city)
            logger.error(f"Erro HTTP ao buscar previsão: {e}")
            raise WeatherAPIException(f"Erro HTTP: {e.response.status_code}", e)

        except RequestException as e:
            logger.error(f"Erro de requisição ao buscar previsão: {e}")
            raise WeatherAPIException(f"Erro de requisição: {str(e)}", e)

        except ValidationError as e:
            logger.error(f"Erro de validação nos dados de previsão: {e}")
            raise WeatherAPIException(f"Dados inválidos da API: {str(e)}", e)

        except (KeyError, ValueError) as e:
            logger.error(f"Formato de dados inválido da API: {e}")
            raise WeatherAPIException(f"Formato de dados inválido: {str(e)}", e)
