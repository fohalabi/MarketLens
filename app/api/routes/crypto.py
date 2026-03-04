from fastapi import APIRouter, HTTPException
from app.core.fetcher import fetch_crypto, fetch_crypto_history
from app.core.analyzer import analyze_crypto, generate_signal

router = APIRouter(
    prefix="/crypto",
    tags=["Crypto"]
)


@router.get("/{symbol}")
def get_crypto(symbol: str, exchange: str = "binance"):
    """
    Get current crypto price and market data.
    - symbol: trading pair e.g. BTC/USDT, ETH/USDT
    - exchange: binance, coinbase, kraken (default: binance)
    """
    try:
        data = fetch_crypto(symbol, exchange_id=exchange)
        return data
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{symbol}/history")
def get_crypto_history(symbol: str, timeframe: str = "1d", limit: int = 30):
    """
    Get historical OHLCV data for a crypto pair.
    - timeframe: 1m, 5m, 15m, 1h, 4h, 1d, 1w
    - limit: number of candles to return (default 30)
    """
    try:
        history = fetch_crypto_history(symbol, timeframe=timeframe, limit=limit)
        return history
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{symbol}/analysis")
def get_crypto_analysis(symbol: str, timeframe: str = "1d", limit: int = 90):
    """
    Get full technical analysis + signal for a crypto pair.
    """
    try:
        analysis = analyze_crypto(symbol, timeframe=timeframe, limit=limit)
        signal = generate_signal(analysis["indicators"])
        return {**analysis, "signal": signal}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))