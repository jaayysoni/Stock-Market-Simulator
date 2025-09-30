# test_ws_client.py
import asyncio
import websockets

async def test_ws():
    uri = "ws://127.0.0.1:8000/ws/stocks"
    async with websockets.connect(uri) as websocket:
        print("✅ Connected to WebSocket")
        try:
            while True:
                message = await websocket.recv()
                print("📈 Stock Update:", message)
        except websockets.ConnectionClosed:
            print("❌ Connection closed")

if __name__ == "__main__":
    asyncio.run(test_ws())