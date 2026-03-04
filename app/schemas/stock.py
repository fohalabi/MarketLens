from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


# Base schema — shared fields between create and response
class StockBase(BaseModel):
    symbol: str
    name: str
    sector: Optional[str] = None


# Schema for creating a stock 
class StockCreate(StockBase):
    pass


# Schema for updating a stock
class StockUpdate(BaseModel):
    current_price: Optional[float] = None
    previous_close: Optional[float] = None
    open_price: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    volume: Optional[float] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    indicators: Optional[Dict[str, Any]] = None


# Schema for the response — what the API sends back
class StockResponse(StockBase):
    id: int
    current_price: Optional[float] = None
    previous_close: Optional[float] = None
    open_price: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    volume: Optional[float] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    indicators: Optional[Dict[str, Any]] = None
    last_updated: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True  