from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False) 
    name = Column(String, nullable=False)                              
    sector = Column(String, nullable=True)                             
    current_price = Column(Float, nullable=True)
    previous_close = Column(Float, nullable=True)
    open_price = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    market_cap = Column(Float, nullable=True)
    pe_ratio = Column(Float, nullable=True)
    indicators = Column(JSON, nullable=True)   # stores RSI, MACD etc as JSON
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())

class StockHistory(Base):
    __tablename__ = "stock_history"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False, index=True)
    date = Column(String, nullable=False)
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    interval = Column(String, nullable=False, default="1d")
    created_at = Column(DateTime, server_default=func.now())

    # Ensure no duplicate entries for same symbol + date + interval
    __table_args__ = (
        __import__('sqlalchemy').UniqueConstraint('symbol', 'date', 'interval', name='uq_stock_history'),
    )