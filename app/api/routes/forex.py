from fastapi import APIRouter, HTTPException
from app.core.fetcher import fetch_forex

router = APIRouter(
    prefix="/forex",
    tags=["Forex"]
)


@router.get("/{from_currency}/{to_currency}")
async def get_forex_rate(from_currency: str, to_currency: str):
    """
    Get forex exchange rate between two currencies.
    - from_currency: e.g. EUR, GBP, JPY
    - to_currency: e.g. USD, EUR, GBP
    Example: /api/forex/EUR/USD
    """
    try:
        data = await fetch_forex(from_currency, to_currency)
        return data
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))