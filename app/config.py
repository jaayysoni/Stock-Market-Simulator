from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL","sqlite:///./stock_simulator.db")

API_KEY = os.getenv("API_KEY","your-default-api-key")

DEBUG = os.getenv("DEBUG","false").lower() == "true"

