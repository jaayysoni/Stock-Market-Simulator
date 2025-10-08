# app/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # -------------------------
    # Database
    # -------------------------
    DATABASE_URL: str = "sqlite:///./stock_simulator.db"

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
    # Finnhub API
    # -------------------------
    FINNHUB_API_KEY: str = ""

    # -------------------------
    # Financial Modeling Prep (FMP) API
    # -------------------------
    FMP_API_KEY: str  # <-- mandatory, must be in .env or environment

    # -------------------------
    # Pydantic config
    # -------------------------
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "forbid",  # Do not allow unknown env vars
    }

# Instantiate global settings object
settings = Settings()