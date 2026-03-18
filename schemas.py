from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CurrentWeather(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "temperature": 34.5,
            "description": "Céu nublado",
            "city": "São Paulo",
            "timestamp": "2026-03-17T10:30:00"
        }
    })

    temperature: float = Field(..., description="Température em Celsius", gt=-50, lt=60)
    description: str = Field(..., description="Descrição do clima", min_length=1, max_length=200)
    city: str = Field(..., description="Nome da cidade", min_length=1, max_length=100)
    timestamp: datetime = Field(default_factory=datetime.now, description="Data e hora da leitura do clima")

    @field_validator("description", "city", mode="before")
    @classmethod
    def clean_strings(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value


class ForecastDay(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "date": "17/03",
            "avg_temp": 32.0
        }
    })

    date: str = Field(..., description="Data no formato DD/MM", min_length=5, max_length=5)
    avg_temp: float = Field(..., description="Temperatura média do dia", gt=-50, lt=60)


class Forecast(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "city": "São Paulo",
            "forecast_days": [
                {"date": "17/03", "avg_temp": 32.0},
                {"date": "18/03", "avg_temp": 25.0}
            ]
        }
    })

    city: str = Field(..., description="Nome da cidade", min_length=1, max_length=100)
    forecast_days: List[ForecastDay] = Field(..., description="Lista de previsões diárias", min_length=1, max_length=5)

    @field_validator("city", mode="before")
    @classmethod
    def clean_strings(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value


class WeatherComment(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "city": "São Paulo",
            "current_weather": {
                "temperature": 34.5,
                "description": "Céu nublado",
                "city": "São Paulo",
                "timestamp": "2026-03-17T10:30:00"
            },
            "forecast": {
                "city": "São Paulo",
                "forecast_days": [
                    {"date": "17/03", "avg_temp": 32.0}
                ]
            }
        }
    })

    city: str = Field(..., description="Nome da cidade", min_length=1, max_length=100)
    current_weather: CurrentWeather = Field(..., description="Dados de clima atual")
    forecast: Forecast = Field(..., description="Previsão do tempo")

    def format_comment(self) -> str:
        today = datetime.now().strftime("%d/%m")
        temp = int(self.current_weather.temperature)
        description = self.current_weather.description.lower()

        forecast_parts = [
            f"{int(f.avg_temp)}°C em {f.date}" for f in self.forecast.forecast_days
        ]

        if len(forecast_parts) == 1:
            forecast_str = forecast_parts[0]
        else:
            forecast_str = ", ".join(forecast_parts[:-1]) + " e " + forecast_parts[-1]

        comment = (
            f"{temp}°C e {description} em {self.city} em {today}. "
            f"Média para os próximos dias: {forecast_str}."
        )
        return comment
