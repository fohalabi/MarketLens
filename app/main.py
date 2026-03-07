from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import api_router
from app.database_init import init_db
from app.websockets.price_stream import manager, stream_prices
import json

# create the FastAPI instance
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Real-time market intelligence, one lens at a time.",
    doc_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # To be adjusted in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all API routes
app.include_router(api_router)

# Initialize the database tables on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Root endpoint
@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.APP_ENV
    }

@app.websocket("/ws/prices")
async def websocket_prices(websocket: WebSocket):
    """
    Websocket endpoint for live price streaming.
    Connect from Streamlit or any frontend like this:
    ws://localhost:8000/ws/prices 
    Send a message with the symbols to track: 
    {
        "symbols": ["AAPL", "GOOGL", "BTC-USD"]
    }
    """
    await manager.connect(websocket)
    try: 
        # Wait for the client to send the symbols to track
        data = await websocket.receive_text()
        message = json.loads(data)
        symbols = message.get("symbols", ["AAPL", "MSFT", "TSLA"])

        # Start streaming prices
        await stream_prices(websocket, symbols)

    except WebSocketDisconnect:
        manager.disconnect(websocket)