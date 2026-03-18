import logging
from typing import Dict
from pydantic import ValidationError
from exceptions import WeatherCommentAPIException
from schemas import WeatherComment
from weather_sdk import OpenWeatherMapSDK
from github_service import GitHubService


logger = logging.getLogger(__name__)


class WeatherCommentService:
    def __init__(
        self,
        weather_sdk: OpenWeatherMapSDK,
        github_service: GitHubService,
    ) -> None:
        self.weather_sdk = weather_sdk
        self.github_service = github_service
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


    def create_weather_gist(self, city: str) -> Dict:
        logger.info(f"Criando novo gist com comentário de clima para: {city}")

        try:
            weather_comment = self.create_weather_comment(city)
            comment_text = weather_comment.format_comment()

            gist_info = self.github_service.create_gist_with_comment(city, comment_text)

            logger.info(f"Gist criado com sucesso para {city}: {gist_info['id']}")

            return gist_info

        except WeatherCommentAPIException:
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao criar gist: {e}")
            raise WeatherCommentAPIException(
                f"Falha ao criar gist: {str(e)}",
                details={"city": city},
            )
