from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    TMDB_API_KEY: str
    TMDB_BASE_URL: str = "https://api.themoviedb.org/3"
    # REDIS_URL: str = "redis://localhost:6379"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    FAST2SMS_API_KEY: str = ""
    OTP_EXPIRE_MINUTES: int = 10

    GMAIL_ADDRESS: str = ""
    GMAIL_APP_PASSWORD: str = ""  

class Config:
        env_file = ".env"

settings = Settings()