from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "development"
    SECRET_KEY: str = "super-secret-jwt-key-change-in-production"
    DATABASE_URL: str = "sqlite:///./capstone.db"
    RATE_LIMIT_SUBMISSIONS: str = "5/minute"
    
    class Config:
        env_file = ".env"

settings = Settings()