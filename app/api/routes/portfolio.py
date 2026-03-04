from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.portfolio import PortfolioCreate, PortfolioResponse
from app.services.portfolio_service import get_portfolio, add_to_portfolio, remove_from_portfolio

router = APIRouter(
    prefix="/portfolio",
    tags=["Portfolio"]
)

# Temporary hardcoded user_id until we add JWT auth
# We'll replace this with the actual logged-in user in Phase 4
TEMP_USER_ID = 1


@router.get("/")
def read_portfolio(db: Session = Depends(get_db)):
    """Get full portfolio with live prices and P&L summary."""
    try:
        portfolio = get_portfolio(db, TEMP_USER_ID)
        return portfolio
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/")
def add_holding(data: PortfolioCreate, db: Session = Depends(get_db)):
    """
    Add a new asset to the portfolio.
    Body: { symbol, asset_type, quantity, buy_price }
    """
    try:
        holding = add_to_portfolio(db, TEMP_USER_ID, data)
        return {"message": "Added to portfolio", "holding": holding}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{holding_id}")
def remove_holding(holding_id: int, db: Session = Depends(get_db)):
    """Remove an asset from the portfolio."""
    success = remove_from_portfolio(db, TEMP_USER_ID, holding_id)
    if not success:
        raise HTTPException(status_code=404, detail="Holding not found")
    return {"message": "Removed from portfolio"}