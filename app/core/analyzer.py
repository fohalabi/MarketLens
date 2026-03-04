from app.core.fetcher import fetch_stock_history, fetch_crypto_history
from app.core.indicators import run_all_indicators
from typing import Dict, Any


def analyze_stock(symbol: str, period: str = "3mo") -> Dict[str, Any]:
    """
    Full analysis pipeline for a stock.
    Fetches historical data and runs all indicators.
    """
    try:
        # Step 1 — Fetch historical data
        history = fetch_stock_history(symbol, period=period)

        # Step 2 — Run all indicators on the data
        indicators = run_all_indicators(history["data"])

        # Step 3 — Return combined result
        return {
            "symbol": symbol.upper(),
            "period": period,
            "indicators": indicators,
            "data_points": len(history["data"]),
            "latest_close": history["data"][-1]["close"] if history["data"] else None,
            "latest_date": history["data"][-1]["date"] if history["data"] else None,
        }
    except Exception as e:
        raise Exception(f"Analysis failed for {symbol}: {str(e)}")


def analyze_crypto(symbol: str, timeframe: str = "1d", limit: int = 90) -> Dict[str, Any]:
    """
    Full analysis pipeline for a crypto pair.
    Fetches historical data and runs all indicators.
    """
    try:
        # Step 1 — Fetch historical data
        history = fetch_crypto_history(symbol, timeframe=timeframe, limit=limit)

        # Step 2 — Run all indicators
        indicators = run_all_indicators(history["data"])

        # Step 3 — Return combined result
        return {
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "indicators": indicators,
            "data_points": len(history["data"]),
            "latest_close": history["data"][-1]["close"] if history["data"] else None,
        }
    except Exception as e:
        raise Exception(f"Crypto analysis failed for {symbol}: {str(e)}")


def generate_signal(indicators: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a simple buy/sell/hold signal based on indicators.
    This is a basic rule-based signal — not financial advice!
    """
    signals = []
    score = 0  # positive = bullish, negative = bearish

    # RSI signal
    rsi = indicators.get("rsi")
    if rsi:
        if rsi < 30:
            signals.append("RSI oversold — potential buy")
            score += 2
        elif rsi > 70:
            signals.append("RSI overbought — potential sell")
            score -= 2
        else:
            signals.append("RSI neutral")

    # MACD signal
    macd = indicators.get("macd", {})
    histogram = macd.get("histogram")
    if histogram:
        if histogram > 0:
            signals.append("MACD bullish crossover")
            score += 1
        else:
            signals.append("MACD bearish crossover")
            score -= 1

    # Bollinger Bands signal
    bb = indicators.get("bollinger_bands", {})
    latest_close = indicators.get("sma_20")
    if bb and latest_close:
        if latest_close <= bb.get("lower", 0):
            signals.append("Price at lower Bollinger Band — potential bounce")
            score += 1
        elif latest_close >= bb.get("upper", 0):
            signals.append("Price at upper Bollinger Band — potential pullback")
            score -= 1

    # Overall signal based on score
    if score >= 2:
        overall = "BUY"
    elif score <= -2:
        overall = "SELL"
    else:
        overall = "HOLD"

    return {
        "overall_signal": overall,
        "score": score,
        "signals": signals
    }