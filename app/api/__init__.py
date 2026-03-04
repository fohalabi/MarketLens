from fastapi import APIRouter
from app.api.routes import stocks, crypto, forex, commodities, portfolio, alerts

# Master router — like an Express router that includes all sub-routers
api_router = APIRouter(prefix="/api")

api_router.include_router(stocks.router)
api_router.include_router(crypto.router)
api_router.include_router(forex.router)
api_router.include_router(commodities.router)
api_router.include_router(portfolio.router)
api_router.include_router(alerts.router)