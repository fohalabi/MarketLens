from sqlalchemy.orm import Session
from app.models.stock import Stock, StockHistory
from app.schemas.stock import StockCreate, StockUpdate
from app.core.fetcher import fetch_stock, fetch_stock_history
from app.core.analyzer import analyze_stock, generate_signal
from typing import Optional, List


def get_or_create_stock(db: Session, symbol: str) -> Stock:
    """
    Fetch stock from DB if it exists, otherwise fetch from
    Yahoo Finance and save it first.
    Like a findOrCreate in Mongoose.
    """
    # Check if stock exists in DB
    stock = db.query(Stock).filter(Stock.symbol == symbol.upper()).first()

    if not stock:
        # Fetch from Yahoo Finance
        data = fetch_stock(symbol)

        # Save to DB
        stock = Stock(
            symbol=data["symbol"],
            name=data["name"],
            sector=data.get("sector"),
            current_price=data.get("current_price"),
            previous_close=data.get("previous_close"),
            open_price=data.get("open_price"),
            high=data.get("high"),
            low=data.get("low"),
            volume=data.get("volume"),
            market_cap=data.get("market_cap"),
            pe_ratio=data.get("pe_ratio"),
        )
        db.add(stock)
        db.commit()
        db.refresh(stock)

    return stock


def refresh_stock(db: Session, symbol: str) -> Stock:
    """
    Force refresh stock data from Yahoo Finance
    and update the DB record.
    """
    data = fetch_stock(symbol)
    stock = db.query(Stock).filter(Stock.symbol == symbol.upper()).first()

    if not stock:
        return get_or_create_stock(db, symbol)

    # Update fields
    stock.current_price = data.get("current_price")
    stock.previous_close = data.get("previous_close")
    stock.open_price = data.get("open_price")
    stock.high = data.get("high")
    stock.low = data.get("low")
    stock.volume = data.get("volume")
    stock.market_cap = data.get("market_cap")
    stock.pe_ratio = data.get("pe_ratio")

    db.commit()
    db.refresh(stock)
    return stock


def get_stock_analysis(db: Session, symbol: str, period: str = "3mo") -> dict:
    """
    Get full stock data + technical analysis + signal.
    This is the main function called by the API route.
    """
    # Get or create stock in DB
    stock = get_or_create_stock(db, symbol)

    # Run technical analysis
    analysis = analyze_stock(symbol, period=period)
    signal = generate_signal(analysis["indicators"])

    return {
        "symbol": stock.symbol,
        "name": stock.name,
        "sector": stock.sector,
        "current_price": stock.current_price,
        "previous_close": stock.previous_close,
        "open_price": stock.open_price,
        "high": stock.high,
        "low": stock.low,
        "volume": stock.volume,
        "market_cap": stock.market_cap,
        "pe_ratio": stock.pe_ratio,
        "analysis": {
            "period": period,
            "indicators": analysis["indicators"],
            "signal": signal,
            "data_points": analysis["data_points"],
            "latest_date": analysis["latest_date"],
        }
    }


def get_all_stocks(db: Session) -> List[Stock]:
    """Get all stocks stored in the database."""
    return db.query(Stock).all()


def save_stock_history(db: Session, symbol: str, period: str = "1mo", interval: str = "1d") -> dict:
    """
    Fetch historical data and store it in PostgreSQL.
    Skips duplicates automatically using the unique constraint.
    """
    history = fetch_stock_history(symbol, period=period, interval=interval)

    saved_count = 0
    skipped_count = 0

    for record in history["data"]:
        # Check if record already exists
        existing = db.query(StockHistory).filter(
            StockHistory.symbol == symbol.upper(),
            StockHistory.date == record["date"],
            StockHistory.interval == interval
        ).first()

        if not existing:
            entry = StockHistory(
                symbol=symbol.upper(),
                date=record["date"],
                open=record["open"],
                high=record["high"],
                low=record["low"],
                close=record["close"],
                volume=record["volume"],
                interval=interval
            )
            db.add(entry)
            saved_count += 1
        else:
            skipped_count += 1

    db.commit()

    return {
        "symbol": symbol.upper(),
        "period": period,
        "interval": interval,
        "saved": saved_count,
        "skipped": skipped_count,
        "total": len(history["data"])
    }


def get_stored_history(db: Session, symbol: str, interval: str = "1d") -> list:
    """
    Retrieve stored historical data from PostgreSQL.
    Falls back to fetching from Yahoo Finance if no data in DB.
    """
    records = db.query(StockHistory).filter(
        StockHistory.symbol == symbol.upper(),
        StockHistory.interval == interval
    ).order_by(StockHistory.date).all()

    if not records:
        return []

    return [
        {
            "date": r.date,
            "open": r.open,
            "high": r.high,
            "low": r.low,
            "close": r.close,
            "volume": r.volume
        }
        for r in records
    ]