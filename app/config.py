# app/config.py

from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pathlib import Path
import os

# Load .env file explicitly
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./stock_simulator.db"

    # API key for internal use
    API_KEY: str = os.getenv("API_KEY", "your-default-api-key")

    # Debug mode
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()