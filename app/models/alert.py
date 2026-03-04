from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    symbol = Column(String, nullable=False)          
    asset_type = Column(String, nullable=False)      
    condition = Column(String, nullable=False)       
    target_price = Column(Float, nullable=False)     
    current_price = Column(Float, nullable=True)     
    is_active = Column(Boolean, default=True)        
    is_triggered = Column(Boolean, default=False)    
    triggered_at = Column(DateTime, nullable=True)   
    created_at = Column(DateTime, server_default=func.now())