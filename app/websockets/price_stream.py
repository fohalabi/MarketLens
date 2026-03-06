from fastapi import WebSocket, WebSocketDisconnect
from app.core.fetcher import fetch_stock, fetch_crypto
import asyncio
import json


class ConnectionManager:
    """
    Manages all active WebSocket connections.
    Like socket.io's connection manager in Node.js.
    """
    def __init__(self):
        # List of all active connections
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to a specific client."""
        await websocket.send_text(json.dumps(message))

    async def broadcast(self, message: dict):
        """Send message to ALL connected clients."""
        for connection in self.active_connections:
            await connection.send_text(json.dumps(message))


# Single instance shared across the app
manager = ConnectionManager()


async def stream_prices(websocket: WebSocket, symbols: list[str], interval: int = 5):
    """
    Streams live prices for given symbols every N seconds.
    Like setInterval in JavaScript but async.
    """
    while True:
        prices = {}

        for symbol in symbols:
            try:
                # Try fetching as stock first
                data = fetch_stock(symbol)
                prices[symbol] = {
                    "symbol": symbol,
                    "price": data.get("current_price"),
                    "change": data.get("current_price", 0) - data.get("previous_close", 0),
                    "type": "stock"
                }
            except Exception as e:
                prices[symbol] = {
                    "symbol": symbol,
                    "error": str(e),
                    "type": "unknown"
                }

        # Send prices to the connected client
        await manager.send_personal_message({
            "type": "price_update",
            "data": prices
        }, websocket)

        # Wait before next update — like setTimeout in JS
        await asyncio.sleep(interval)