import logging
from pydantic import ValidationError
from exceptions import WeatherCommentAPIException
from schemas import WeatherComment
from weather_sdk import OpenWeatherMapSDK

logger = logging.getLogger(__name__)


class WeatherCommentService:
    def __init__(
        self,
        weather_sdk: OpenWeatherMapSDK,
    ) -> None:
        self.weather_sdk = weather_sdk
        logger.debug("Serviço WeatherComment inicializado")

    def create_weather_comment(self, city: str) -> WeatherComment:
        logger.info(f"Criando comentário de clima para cidade: {city}")

        try:
            current_weather = self.weather_sdk.get_current_weather(city)
            forecast = self.weather_sdk.get_forecast(city, days=5)

            weather_comment = WeatherComment(
                city=city, current_weather=current_weather, forecast=forecast
            )

            logger.debug(
                f"Comentário de clima criado com sucesso para {city}"
            )
            return weather_comment

        except WeatherCommentAPIException:
            raise
        except ValidationError as e:
            logger.error(f"Erro de validação ao criar comentário de clima: {e}")
            raise WeatherCommentAPIException(
                f"Dados inválidos: {str(e)}", 
                error_code="VALIDATION_ERROR",
                status_code=422,
                details={"city": city}
            )
        except Exception as e:
            logger.error(f"Erro inesperado ao criar comentário de clima: {e}")
            raise WeatherCommentAPIException(
                f"Falha ao criar comentário de clima: {str(e)}", 
                details={"city": city}
            )
