# app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path
from dotenv import load_dotenv

# -------------------------
# Load .env file manually
# -------------------------
BASE_DIR = Path(__file__).parent.parent  # project root
load_dotenv(dotenv_path=BASE_DIR / ".env")  # ensures env variables are loaded

class Settings(BaseSettings):
    # -------------------------
    # Internal API key
    # -------------------------
    API_KEY: str = "your-default-api-key"

    # -------------------------
    # Debug mode
    # -------------------------
    DEBUG: bool = False

    # -------------------------
    # JWT settings
    # -------------------------
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # -------------------------
    # Google OAuth
    # -------------------------
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"

    # -------------------------
    # Finnhub API keys
    # -------------------------
    FINNHUB_API_KEY_1: str = Field(..., env="FINNHUB_API_KEY_1")    # WebSocket key
    FINNHUB_API_KEY_2: str = Field(..., env="FINNHUB_API_KEY_2")  # REST API key

    # -------------------------
    # Database URLs
    # -------------------------
    USER_DB_URL: str = Field(default="sqlite:///./user_data.db", env="USER_DB_URL")
    MARKET_DB_URL: str = Field(default="sqlite:///./market_data.db", env="MARKET_DB_URL")

    # -------------------------
    # Pydantic config
    # -------------------------
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",  # load .env from project root
        env_file_encoding="utf-8",
        extra="ignore"  # ✅ ignore unknown .env fields safely
    )


# -------------------------
# Instantiate global settings object
# -------------------------
settings = Settings()