from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.market_service import get_stock_analysis, get_all_stocks, refresh_stock, save_stock_history, get_stored_history
from app.core.fetcher import fetch_stock_history

router = APIRouter(
    prefix="/stocks",
    tags=["Stocks"]  # groups endpoints in Swagger UI
)


@router.get("/")
def get_stocks(db: Session = Depends(get_db)):
    """Get all stocks stored in the database."""
    stocks = get_all_stocks(db)
    return {"stocks": stocks, "count": len(stocks)}


@router.get("/{symbol}")
def get_stock(symbol: str, period: str = "3mo", db: Session = Depends(get_db)):
    """
    Get full stock data + technical analysis + signal.
    - symbol: stock ticker e.g. AAPL, TSLA, MSFT
    - period: 1mo, 3mo, 6mo, 1y (default 3mo)
    """
    try:
        result = get_stock_analysis(db, symbol, period)
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{symbol}/history")
def get_stock_history(
    symbol: str,
    period: str = "1mo",
    interval: str = "1d"
):
    """
    Get historical OHLCV data for charting.
    - period: 1d, 5d, 1mo, 3mo, 6mo, 1y
    - interval: 1m, 5m, 15m, 1h, 1d, 1wk
    """
    try:
        history = fetch_stock_history(symbol, period=period, interval=interval)
        return history
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{symbol}/refresh")
def refresh_stock_data(symbol: str, db: Session = Depends(get_db)):
    """Force refresh stock data from Yahoo Finance."""
    try:
        stock = refresh_stock(db, symbol)
        return {"message": f"{symbol.upper()} refreshed successfully", "stock": stock}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{symbol}/history/save")
def save_history(
    symbol: str,
    period: str = "1mo",
    interval: str = "1d",
    db: Session = Depends(get_db)
):
    """
    Fetch and store historical data for a stock in PostgreSQL.
    - period: 1mo, 3mo, 6mo, 1y
    - interval: 1d, 1wk
    """
    try:
        result = save_stock_history(db, symbol, period=period, interval=interval)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{symbol}/history/stored")
def get_history_from_db(
    symbol: str,
    interval: str = "1d",
    db: Session = Depends(get_db)
):
    """
    Retrieve stored historical data from PostgreSQL.
    """
    try:
        records = get_stored_history(db, symbol, interval=interval)
        if not records:
            raise HTTPException(
                status_code=404,
                detail=f"No stored history for {symbol}. Call POST /{symbol}/history/save first."
            )
        return {
            "symbol": symbol.upper(),
            "interval": interval,
            "count": len(records),
            "data": records
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))