import os
from typing import Generator
import pytest
from config import Config


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment() -> None:
    os.environ["OPENWEATHER_API_KEY"] = "test_api_key_123"
    os.environ["GITHUB_TOKEN"] = "test_github_token_456"
    os.environ["DEBUG"] = "True"


@pytest.fixture
def clear_env_keys(monkeypatch) -> Generator:
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    yield
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test_api_key_123")
    monkeypatch.setenv("GITHUB_TOKEN", "test_github_token_456")


@pytest.fixture
def test_config(monkeypatch) -> Config:
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test_api_key_123")
    monkeypatch.setenv("GITHUB_TOKEN", "test_github_token_456")
    return Config()
