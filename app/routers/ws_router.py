# app/routers/ws_router.py

import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import redis.asyncio as redis

router = APIRouter()

REDIS_URL = "redis://localhost"
connected_clients = set()

@router.websocket("/stocks")  # <- no extra /ws
async def stocks_ws(websocket: WebSocket):
    """
    WebSocket endpoint for live stock updates.
    JWT temporarily removed for testing.
    """
    await websocket.accept()
    connected_clients.add(websocket)

    redis_client = redis.from_url(REDIS_URL)
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("stocks:updates")

    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message["type"] == "message":
                data = message["data"]
                if isinstance(data, bytes):
                    data = data.decode()
                await websocket.send_text(data)

            await asyncio.sleep(0.01)

    except WebSocketDisconnect:
        connected_clients.remove(websocket)

    finally:
        await pubsub.unsubscribe("stocks:updates")
        await websocket.close()