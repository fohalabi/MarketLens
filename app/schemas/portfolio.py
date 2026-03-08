from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class PortfolioBase(BaseModel):
    symbol: str
    asset_type: str     # stock, crypto, forex, commodity
    quantity: float
    buy_price: float


class PortfolioCreate(PortfolioBase):
    pass


class PortfolioUpdate(BaseModel):
    quantity: Optional[float] = None
    buy_price: Optional[float] = None
    current_price: Optional[float] = None
    profit_loss: Optional[float] = None


class PortfolioResponse(PortfolioBase):
    id: int
    user_id: int
    current_price: Optional[float] = None
    profit_loss: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)