from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "sqlite+aiosqlite:///./truthguard.db"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    # Set CORS_ORIGINS="*" to allow all, or comma-separated list of origins
    cors_origins: str = "*"

    # API Keys & External Fact-Checking Integrations
    ai_api_key: str = ""
    search_api_key: str = ""
    google_fact_check_api_key: str = ""
    tavily_api_key: str = ""
    news_api_key: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]

    model_config = {"env_file": ("backend/.env", ".env"), "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()