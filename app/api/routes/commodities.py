from fastapi import APIRouter, HTTPException
from app.core.fetcher import fetch_commodity
from typing import Optional

router = APIRouter(
    prefix="/commodities",
    tags=["Commodities"]
)

# Supported commodity symbols and their friendly names
SUPPORTED_COMMODITIES = {
    "WTI": "West Texas Intermediate Crude Oil",
    "BRENT": "Brent Crude Oil",
    "NATURAL_GAS": "Natural Gas",
    "COPPER": "Copper",
    "ALUMINUM": "Aluminum",
    "WHEAT": "Wheat",
    "CORN": "Corn",
    "COTTON": "Cotton",
    "SUGAR": "Sugar",
    "COFFEE": "Coffee",
}


@router.get("/")
def get_supported_commodities():
    """Get list of all supported commodities."""
    return {
        "commodities": [
            {"symbol": symbol, "name": name}
            for symbol, name in SUPPORTED_COMMODITIES.items()
        ]
    }


@router.get("/{symbol}")
async def get_commodity(symbol: str):
    """
    Get current price for a commodity.
    Supported: WTI, BRENT, NATURAL_GAS, COPPER,
               ALUMINUM, WHEAT, CORN, COTTON, SUGAR, COFFEE
    """
    if symbol.upper() not in SUPPORTED_COMMODITIES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported commodity. Supported: {', '.join(SUPPORTED_COMMODITIES.keys())}"
        )
    try:
        data = await fetch_commodity(symbol)
        return data
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))