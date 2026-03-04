from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class Portfolio(Base):
    __tablename__ = "portfolio"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    symbol = Column(String, nullable=False)        
    asset_type = Column(String, nullable=False)    
    quantity = Column(Float, nullable=False)        
    buy_price = Column(Float, nullable=False)       
    current_price = Column(Float, nullable=True)    
    profit_loss = Column(Float, nullable=True)      
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())