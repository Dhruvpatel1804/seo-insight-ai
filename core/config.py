from typing import List, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

LogLevelName = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    # -------------------------------------------------------------------------
    # Application
    # -------------------------------------------------------------------------
    PROJECT_NAME: str = "SEO Insight AI"
    PROJECT_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # -------------------------------------------------------------------------
    # API server (runtime)
    # -------------------------------------------------------------------------
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = False

    API_DOCS_ENABLED: bool = True
    API_SWAGGER_PATH: str = "/swagger-docs/"
    API_REDOC_PATH: str = "/custom-docs/"

    API_CORS_ORIGINS: str | List[str] = Field(default="*")
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str | List[str] = Field(default="*")
    CORS_ALLOW_HEADERS: str | List[str] = Field(default="*")

    # -------------------------------------------------------------------------
    # Logging
    # -------------------------------------------------------------------------
    LOG_LEVEL: LogLevelName = "INFO"
    LOG_DIR: str = "logs"
    LOG_MAX_BYTES: int = 5_000_000
    LOG_BACKUP_COUNT: int = 5
    LOG_HTTPX_LEVEL: LogLevelName = "WARNING"

    # -------------------------------------------------------------------------
    # OpenAI
    # -------------------------------------------------------------------------
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TEMPERATURE: float = 0.2
    OPENAI_TIMEOUT_SECONDS: int = 60
    OPENAI_MAX_RETRIES: int = 2

    # -------------------------------------------------------------------------
    # Redis cache
    # -------------------------------------------------------------------------
    REDIS_URL: str | None = None
    AUDIT_CACHE_TTL_SECONDS: int = 86_400

    # -------------------------------------------------------------------------
    # Google PageSpeed Insights
    # -------------------------------------------------------------------------
    PAGESPEED_API_KEY: str | None = None
    PAGESPEED_API_URL: str = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    PAGESPEED_TIMEOUT_SECONDS: int = 120
    PAGESPEED_CATEGORY: str = "performance"

    # -------------------------------------------------------------------------
    # HTTP client / security limits
    # -------------------------------------------------------------------------
    HTTP_TIMEOUT_SECONDS: int = 30
    HTTP_USER_AGENT: str = "SEO-Insight-AI/1.0"
    MAX_RESPONSE_BYTES: int = 5_000_000
    MAX_REDIRECTS: int = 5
    MAX_URL_LENGTH: int = 2048

    # -------------------------------------------------------------------------
    # Storage
    # -------------------------------------------------------------------------
    REPORTS_DIR: str = "reports"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        populate_by_name=True,
    )

    @field_validator(
        "API_CORS_ORIGINS",
        "CORS_ALLOW_METHODS",
        "CORS_ALLOW_HEADERS",
        mode="before",
    )
    @classmethod
    def split_comma_separated_list(cls, value: str | List[str]) -> List[str]:
        if isinstance(value, str):
            if value.strip() == "*":
                return ["*"]
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


settings = Settings()
