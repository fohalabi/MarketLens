from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import datetime


class AlertBase(BaseModel):
    symbol: str
    asset_type: str                 # stock, crypto, forex, commodity
    condition: str                  # "above" or "below"
    target_price: float


# Validate that condition is only "above" or "below"
class AlertCreate(AlertBase):
    @field_validator("condition")
    @classmethod
    def condition_must_be_valid(cls, v):
        if v not in ["above", "below"]:
            raise ValueError('condition must be "above" or "below"')
        return v


class AlertUpdate(BaseModel):
    is_active: Optional[bool] = None
    target_price: Optional[float] = None


class AlertResponse(AlertBase):
    id: int
    user_id: int
    current_price: Optional[float] = None
    is_active: bool
    is_triggered: bool
    triggered_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)