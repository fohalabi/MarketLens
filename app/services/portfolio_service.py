from sqlalchemy.orm import Session
from app.models.portfolio import Portfolio
from app.schemas.portfolio import PortfolioCreate, PortfolioUpdate
from app.core.fetcher import fetch_stock, fetch_crypto
from typing import List, Optional


def calculate_profit_loss(buy_price: float, current_price: float, quantity: float) -> float:
    """Calculate profit or loss for a position."""
    return round((current_price - buy_price) * quantity, 4)


def calculate_return_percent(buy_price: float, current_price: float) -> float:
    """Calculate percentage return on a position."""
    return round(((current_price - buy_price) / buy_price) * 100, 4)


def get_portfolio(db: Session, user_id: int) -> dict:
    """
    Get full portfolio for a user with live prices and P&L.
    """
    holdings = db.query(Portfolio).filter(Portfolio.user_id == user_id).all()

    total_invested = 0
    total_current_value = 0
    enriched_holdings = []

    for holding in holdings:
        # Fetch live price based on asset type
        try:
            if holding.asset_type == "stock":
                data = fetch_stock(holding.symbol)
                current_price = data.get("current_price", holding.buy_price)
            elif holding.asset_type == "crypto":
                data = fetch_crypto(holding.symbol)
                current_price = data.get("current_price", holding.buy_price)
            else:
                current_price = holding.current_price or holding.buy_price
        except:
            current_price = holding.current_price or holding.buy_price

        invested = holding.buy_price * holding.quantity
        current_value = current_price * holding.quantity
        profit_loss = calculate_profit_loss(holding.buy_price, current_price, holding.quantity)
        return_pct = calculate_return_percent(holding.buy_price, current_price)

        total_invested += invested
        total_current_value += current_value

        enriched_holdings.append({
            "id": holding.id,
            "symbol": holding.symbol,
            "asset_type": holding.asset_type,
            "quantity": holding.quantity,
            "buy_price": holding.buy_price,
            "current_price": current_price,
            "invested": round(invested, 2),
            "current_value": round(current_value, 2),
            "profit_loss": profit_loss,
            "return_percent": return_pct,
        })

    total_profit_loss = round(total_current_value - total_invested, 2)
    total_return_pct = round(((total_current_value - total_invested) / total_invested) * 100, 2) if total_invested > 0 else 0

    return {
        "user_id": user_id,
        "holdings": enriched_holdings,
        "summary": {
            "total_invested": round(total_invested, 2),
            "total_current_value": round(total_current_value, 2),
            "total_profit_loss": total_profit_loss,
            "total_return_percent": total_return_pct,
            "number_of_holdings": len(holdings),
        }
    }


def add_to_portfolio(db: Session, user_id: int, data: PortfolioCreate) -> Portfolio:
    """Add a new asset to the portfolio."""
    holding = Portfolio(
        user_id=user_id,
        symbol=data.symbol.upper(),
        asset_type=data.asset_type,
        quantity=data.quantity,
        buy_price=data.buy_price,
    )
    db.add(holding)
    db.commit()
    db.refresh(holding)
    return holding


def remove_from_portfolio(db: Session, user_id: int, holding_id: int) -> bool:
    """Remove an asset from the portfolio."""
    holding = db.query(Portfolio).filter(
        Portfolio.id == holding_id,
        Portfolio.user_id == user_id
    ).first()

    if not holding:
        return False

    db.delete(holding)
    db.commit()
    return True