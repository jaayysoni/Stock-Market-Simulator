# app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path
from dotenv import load_dotenv

# -------------------------
# Load .env file manually
# -------------------------
BASE_DIR = Path(__file__).parent.parent  # project root
load_dotenv(dotenv_path=BASE_DIR / ".env")

class Settings(BaseSettings):
    # Debug mode
    DEBUG: bool = Field(default=False, env="DEBUG")

    # JWT settings (if still needed for internal token)
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Binance / Crypto API
    BINANCE_API_KEY: str = Field(..., env="BINANCE_API_KEY")
    BINANCE_API_SECRET: str = Field(..., env="BINANCE_API_SECRET")
    BINANCE_WS_URL: str = Field(..., env="BINANCE_WS_URL")

    # Database URLs
    USER_DB_URL: str = Field(default="sqlite:///./user_data.db", env="USER_DB_URL")

    # Pydantic config
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instantiate global settings object
settings = Settings()