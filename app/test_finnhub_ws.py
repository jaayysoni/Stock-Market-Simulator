import os
import asyncio
import websockets
import json
from dotenv import load_dotenv

# Load .env
load_dotenv()

FINNHUB_WS = f"wss://ws.finnhub.io?token={os.getenv('FINNHUB_API_KEY')}"

async def test_finnhub_ws():
    async with websockets.connect(FINNHUB_WS) as ws:
        # Subscribe to multiple stocks at once
        symbols = ["AAPL", "TCS.NS", "INFY.NS", "RELIANCE.NS"]
        for symbol in symbols:
            await ws.send(json.dumps({"type": "subscribe", "symbol": symbol}))
            print(f"✅ Subscribed to {symbol}")

        # Listen indefinitely (or you can limit with a counter)
        count = 0
        while count < 20:  # listen for 20 messages then stop
            msg = await ws.recv()
            data = json.loads(msg)
            print("WS Message:", data)
            count += 1

asyncio.run(test_finnhub_ws())