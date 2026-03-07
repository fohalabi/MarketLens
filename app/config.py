from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "MarketLens"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql://postgres:password@db:5432/marketlensdb"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "marketlensdb"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # JWT Auth
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Market Data APIs
    ALPHA_VANTAGE_API_KEY: str = ""
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_SECRET_KEY: Optional[str] = None

    model_config = ConfigDict(env_file=".env", case_sensitive=True) 


settings = Settings()