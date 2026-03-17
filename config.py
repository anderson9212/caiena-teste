import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    OPENWEATHER_API_KEY: Optional[str] = os.getenv("OPENWEATHER_API_KEY")
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
    OPENWEATHER_BASE_URL: str = os.getenv("OPENWEATHER_API_URL", "https://api.openweathermap.org/data/2.5")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    @classmethod
    def validate(cls) -> None:
        if not cls.OPENWEATHER_API_KEY:
            raise ValueError("OPENWEATHER_API_KEY é obrigatória")

        if not cls.OPENWEATHER_API_KEY.strip():
            raise ValueError("OPENWEATHER_API_KEY não pode estar vazia")

        if not cls.GITHUB_TOKEN:
            raise ValueError("GITHUB_TOKEN é obrigatória")
        
        if not cls.GITHUB_TOKEN.strip():
            raise ValueError("GITHUB_TOKEN não pode estar vazia")
