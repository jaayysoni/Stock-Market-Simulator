import asyncio
from app.services.crypto_ws import CryptoWebSocket

# List your 90 coins here
COINS = [
    "btcusdt", "ethusdt", "solusdt", "adausdt", "xrpusdt",
    # ... add the remaining coins
]

async def start_ws_task():
    ws_manager = CryptoWebSocket(COINS)
    await ws_manager.start()

def start_background_tasks(app):
    """Attach background tasks to the FastAPI app"""
    @app.on_event("startup")
    async def startup_tasks():
        asyncio.create_task(start_ws_task())