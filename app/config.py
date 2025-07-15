from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pathlib import Path

#Load .env file explicitly
env_path = Path('.') / '.env'
load_dotenv(dotenv_path = env_path)

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./stock_simulator.db"
    API_KEY: str = "your-default-api-key"
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()