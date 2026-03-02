from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200   # 30 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # TMDB
    TMDB_API_KEY: str
    TMDB_BASE_URL: str = "https://api.themoviedb.org/3"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # App
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    class Config:
        env_file = ".env"

# One instance used everywhere — import this, not the class
settings = Settings()