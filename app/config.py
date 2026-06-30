"""
Centerlized Configration
Used pydantic-settings for validation environment variables.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM configration
    # can add open ai llm , anthropic llm but i have added gemini as it was free
    # can add different models

    primary_model: str = "gemini-2.5-flash"
    fallback_model: str = "gemini-2.5-flash"

    # Langsmith
    langsmith_tracing_v2: bool = True
    langsmith_api_key: str = ""
    langsmith_project: str = "production-api"

    # Application
    app_env: str = "development"
    log_level: str = "INFO"
    rate_limit: str = "20/minute"
    cache_ttl_seconds: int = 300
    max_retries: int = 3

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instances - loaded once, reused everywhere."""
    return Settings()
