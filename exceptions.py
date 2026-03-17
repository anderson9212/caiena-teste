from typing import Optional


class WeatherCommentAPIException(Exception):
    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[dict] = None,
    ) -> None:
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict:
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class WeatherAPIException(WeatherCommentAPIException):
    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        details: Optional[dict] = None,
    ) -> None:
        super().__init__(
            message=message,
            error_code="WEATHER_API_ERROR",
            status_code=502,
            details=details,
        )
        self.original_error = original_error


class CityNotFoundError(WeatherCommentAPIException):
    def __init__(self, city: str) -> None:
        super().__init__(
            message=f"Cidade não encontrada: {city}",
            error_code="CITY_NOT_FOUND",
            status_code=404,
            details={"city": city},
        )


class GitHubAPIException(WeatherCommentAPIException):
    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        details: Optional[dict] = None,
    ) -> None:
        super().__init__(
            message=message,
            error_code="GITHUB_API_ERROR",
            status_code=502,
            details=details,
        )
        self.original_error = original_error


class GistNotFoundError(WeatherCommentAPIException):
    def __init__(self, gist_id: str) -> None:
        super().__init__(
            message=f"Gist não encontrado: {gist_id}",
            error_code="GIST_NOT_FOUND",
            status_code=404,
            details={"gist_id": gist_id},
        )


class InvalidConfigurationError(WeatherCommentAPIException):
    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(
            message=message,
            error_code="INVALID_CONFIGURATION",
            status_code=500,
            details=details,
        )


class ValidationError(WeatherCommentAPIException):
    def __init__(self, field: str, message: str) -> None:
        super().__init__(
            message=f"Erro de validação em {field}: {message}",
            error_code="VALIDATION_ERROR",
            status_code=422,
            details={"field": field, "message": message},
        )
