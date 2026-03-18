import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
from config import Config
from exceptions import WeatherCommentAPIException
from weather_sdk import OpenWeatherMapSDK
from weather_service import WeatherCommentService
from github_service import GitHubService

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


class GistCommentResponse(BaseModel):
    gist_id: str
    gist_url: str
    comment: str
    city: str
    created_at: str


try:
    weather_sdk = OpenWeatherMapSDK()
    github_service = GitHubService()
    weather_service = WeatherCommentService(weather_sdk, github_service)
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


@app.post("/weather-comment/{city}", response_model=GistCommentResponse, tags=["Weather Comments"])
async def create_weather_comment_gist(
    city: str = Path(..., description="Nome da cidade", min_length=1),
) -> GistCommentResponse:
    logger.info(f"Requisição de criar gist com comentário de clima: {city}")
    
    if not weather_service:
        logger.error("Serviço não inicializado")
        raise HTTPException(status_code=500, detail="Serviço não inicializado")
    
    try:
        gist_info = weather_service.create_weather_gist(city)
        logger.info(f"Gist criado com sucesso para {city}")
        
        return GistCommentResponse(
            gist_id=gist_info["id"],
            gist_url=gist_info["url"],
            comment=gist_info["comment"],
            city=city,
            created_at=str(gist_info["created_at"]),
        )
    
    except WeatherCommentAPIException as e:
        logger.warning(f"Falha ao criar gist: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)


if __name__ == "__main__":
    import uvicorn

    logger.info("Iniciando servidor da API de Comentário de Clima")
    uvicorn.run(app, host="0.0.0.0", port=8000)
