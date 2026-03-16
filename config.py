import os
from typing import Optional


class Config:
    OPENWEATHER_API_KEY: Optional[str] = os.getenv("OPENWEATHER_API_KEY")
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
    OPENWEATHER_BASE_URL: Optional[str] = os.getenv("OPENWEATHER_API_URL")

    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    @classmethod
    def validate(cls) -> None:
        if not cls.OPENWEATHER_API_KEY:
            raise ValueError("Variável de ambiente OPENWEATHER_API_KEY é obrigatória")

        if not cls.GITHUB_TOKEN:
            raise ValueError("Variável de ambiente GITHUB_TOKEN é obrigatória")

        if not cls.OPENWEATHER_BASE_URL:
            raise ValueError("Variável de ambiente OPENWEATHER_API_URL é obrigatória")
