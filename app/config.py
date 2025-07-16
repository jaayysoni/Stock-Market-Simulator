# app/config.py

from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pathlib import Path

# Load .env file explicitly
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./stock_simulator.db"
    API_KEY: str = "your-default-api-key"
    DEBUG: bool = False

    # Add JWT settings below
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()