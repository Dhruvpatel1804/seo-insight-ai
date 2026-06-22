from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "my_app"
    PROJECT_VERSION: str = "1.0.0"
    
    ASYNC_DATABASE_URL: str | None = None

    SECRET_KEY: str | None = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    FERNET_SECRET_KEY: str | None = None
    
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"

    HEALTHCHECK_INTERVAL_SECONDS: int = 3600
    
    CORS_ORIGINS: List[str] = ["*"]
    
    # Email settings
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: str | None = None


    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()