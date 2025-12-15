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
    # Debug mode
    # -------------------------
    DEBUG: bool = False

    # -------------------------
    # JWT settings
    # -------------------------
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # -------------------------
    # Google OAuth (if needed)
    # -------------------------
    GOOGLE_CLIENT_ID: str = Field(default="", env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = Field(default="", env="GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: str = Field(default="http://localhost:8000/auth/google-callback", env="GOOGLE_REDIRECT_URI")

    # -------------------------
    # Binance / Crypto API
    # -------------------------
    BINANCE_API_KEY: str = Field(..., env="BINANCE_API_KEY")
    BINANCE_API_SECRET: str = Field(..., env="BINANCE_API_SECRET")
    BINANCE_WS_URL: str = Field(..., env="BINANCE_WS_URL")

    # -------------------------
    # Database URLs
    # -------------------------
    USER_DB_URL: str = Field(default="sqlite:///./user_data.db", env="USER_DB_URL")

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
