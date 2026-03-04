from sqlalchemy.orm import Session
from app.models.stock import Stock
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