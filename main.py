import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
from config import Config
from exceptions import WeatherCommentAPIException
from schemas import WeatherComment
from weather_sdk import OpenWeatherMapSDK
from weather_service import WeatherCommentService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    Config.validate()
    logger.info("Configuração validada com sucesso")
except ValueError as e:
    logger.error(f"Erro de validação de configuração: {e}")
    raise

app = FastAPI(
    title="Caiena Teste - Weather Comment API",
    description="Integra o OpenWeatherMap e o GitHub para publicar comentários meteorológicos em Gists do GitHub",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class HealthResponse(BaseModel):
    status: str
    message: str


class CommentResponse(BaseModel):
    status: str
    message: str
    comment: str
    city: str
    gist_id: str


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[dict] = None


try:
    weather_sdk = OpenWeatherMapSDK()
    weather_service = WeatherCommentService(weather_sdk)
    logger.info("Serviços inicializados com sucesso")
except ValueError as e:
    logger.error(f"Erro de configuração: {e}")
    weather_service = None


@app.exception_handler(WeatherCommentAPIException)
async def weather_comment_exception_handler(request, exc: WeatherCommentAPIException):
    logger.error(f"Exceção da API: {exc.message}")
    return {
        "error": exc.error_code,
        "message": exc.message,
        "details": exc.details,
    }


@app.get("/", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        message="API de Comentário de Clima está funcionando",
    )


@app.get("/weather/{city}", response_model=WeatherComment, tags=["Weather"])
async def get_weather_data(
    city: str = Path(..., description="Nome da cidade", min_length=1),
) -> WeatherComment:
    logger.info(f"Requisição de dados de clima para: {city}")
    
    if not weather_service:
        logger.error("Serviço não inicializado")
        raise HTTPException(status_code=500, detail="Serviço não inicializado")
    
    try:
        weather_comment = weather_service.create_weather_comment(city)
        logger.info(f"Dados de clima obtidos com sucesso para {city}")
        return weather_comment
    
    except WeatherCommentAPIException as e:
        logger.warning(f"Falha ao obter dados de clima: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)


if __name__ == "__main__":
    import uvicorn

    logger.info("Iniciando servidor da API de Comentário de Clima")
    uvicorn.run(app, host="0.0.0.0", port=8000)
