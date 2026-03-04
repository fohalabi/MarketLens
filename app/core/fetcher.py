import yfinance as yf
import ccxt
import httpx
from typing import Optional
from app.config import settings


# STOCKS 

def fetch_stock(symbol: str) -> dict:
    """
    Fetch current stock data from Yahoo Finance.
    No API key needed — yfinance is free and unlimited.
    Example: fetch_stock("AAPL")
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        return {
            "symbol": symbol.upper(),
            "name": info.get("longName", symbol),
            "sector": info.get("sector", None),
            "current_price": info.get("currentPrice", None),
            "previous_close": info.get("previousClose", None),
            "open_price": info.get("open", None),
            "high": info.get("dayHigh", None),
            "low": info.get("dayLow", None),
            "volume": info.get("volume", None),
            "market_cap": info.get("marketCap", None),
            "pe_ratio": info.get("trailingPE", None),
        }
    except Exception as e:
        raise Exception(f"Failed to fetch stock {symbol}: {str(e)}")


def fetch_stock_history(symbol: str, period: str = "1mo", interval: str = "1d") -> dict:
    """
    Fetch historical OHLCV data for a stock.
    period options: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y
    interval options: 1m, 5m, 15m, 1h, 1d, 1wk, 1mo
    """
    try:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period=period, interval=interval)

        # Convert DataFrame to list of dicts — easy to work with
        records = []
        for date, row in history.iterrows():
            records.append({
                "date": str(date),
                "open": round(row["Open"], 4),
                "high": round(row["High"], 4),
                "low": round(row["Low"], 4),
                "close": round(row["Close"], 4),
                "volume": row["Volume"],
            })

        return {
            "symbol": symbol.upper(),
            "period": period,
            "interval": interval,
            "data": records
        }
    except Exception as e:
        raise Exception(f"Failed to fetch history for {symbol}: {str(e)}")


# CRYPTO 

def fetch_crypto(symbol: str, exchange_id: str = "binance") -> dict:
    """
    Fetch current crypto price from an exchange via ccxt.
    Example: fetch_crypto("BTC/USDT")
    """
    try:
        # Initialize the exchange — like connecting to a specific crypto exchange
        exchange_class = getattr(ccxt, exchange_id)
        exchange = exchange_class()

        ticker = exchange.fetch_ticker(symbol)

        return {
            "symbol": symbol.upper(),
            "exchange": exchange_id,
            "current_price": ticker.get("last", None),
            "high": ticker.get("high", None),
            "low": ticker.get("low", None),
            "volume": ticker.get("baseVolume", None),
            "change_24h": ticker.get("change", None),
            "change_percent_24h": ticker.get("percentage", None),
            "bid": ticker.get("bid", None),
            "ask": ticker.get("ask", None),
        }
    except Exception as e:
        raise Exception(f"Failed to fetch crypto {symbol}: {str(e)}")


def fetch_crypto_history(symbol: str, timeframe: str = "1d", limit: int = 30) -> dict:
    """
    Fetch historical OHLCV data for a crypto pair.
    timeframe options: 1m, 5m, 15m, 1h, 4h, 1d, 1w
    """
    try:
        exchange = ccxt.binance()
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

        records = []
        for candle in ohlcv:
            records.append({
                "timestamp": candle[0],
                "open": candle[1],
                "high": candle[2],
                "low": candle[3],
                "close": candle[4],
                "volume": candle[5],
            })

        return {
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "data": records
        }
    except Exception as e:
        raise Exception(f"Failed to fetch crypto history for {symbol}: {str(e)}")


# FOREX

async def fetch_forex(from_currency: str, to_currency: str) -> dict:
    """
    Fetch forex exchange rate from Alpha Vantage.
    Example: fetch_forex("EUR", "USD")
    Requires ALPHA_VANTAGE_API_KEY in .env
    """
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": from_currency.upper(),
            "to_currency": to_currency.upper(),
            "apikey": settings.ALPHA_VANTAGE_API_KEY
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()

        rate_data = data.get("Realtime Currency Exchange Rate", {})

        return {
            "from_currency": from_currency.upper(),
            "to_currency": to_currency.upper(),
            "pair": f"{from_currency.upper()}/{to_currency.upper()}",
            "exchange_rate": float(rate_data.get("5. Exchange Rate", 0)),
            "bid": float(rate_data.get("8. Bid Price", 0)),
            "ask": float(rate_data.get("9. Ask Price", 0)),
            "last_updated": rate_data.get("6. Last Refreshed", None),
        }
    except Exception as e:
        raise Exception(f"Failed to fetch forex {from_currency}/{to_currency}: {str(e)}")


# COMMODITIES

async def fetch_commodity(symbol: str) -> dict:
    """
    Fetch commodity price from Alpha Vantage.
    Supported symbols: WTI (Oil), BRENT, NATURAL_GAS, COPPER, ALUMINUM,
                       WHEAT, CORN, COTTON, SUGAR, COFFEE
    """
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": symbol.upper(),
            "interval": "monthly",
            "apikey": settings.ALPHA_VANTAGE_API_KEY
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()

        # Get the most recent data point
        latest = data.get("data", [{}])[0]

        return {
            "symbol": symbol.upper(),
            "name": data.get("name", symbol),
            "unit": data.get("unit", ""),
            "current_price": float(latest.get("value", 0)),
            "last_updated": latest.get("date", None),
        }
    except Exception as e:
        raise Exception(f"Failed to fetch commodity {symbol}: {str(e)}")