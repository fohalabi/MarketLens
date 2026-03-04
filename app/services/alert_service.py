from sqlalchemy.orm import Session
from app.models.alert import Alert
from app.schemas.alert import AlertCreate
from app.core.fetcher import fetch_stock, fetch_crypto
from typing import List
from datetime import datetime


def get_alerts(db: Session, user_id: int) -> List[Alert]:
    """Get all alerts for a user."""
    return db.query(Alert).filter(Alert.user_id == user_id).all()


def create_alert(db: Session, user_id: int, data: AlertCreate) -> Alert:
    """Create a new price alert."""
    alert = Alert(
        user_id=user_id,
        symbol=data.symbol.upper(),
        asset_type=data.asset_type,
        condition=data.condition,
        target_price=data.target_price,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def delete_alert(db: Session, user_id: int, alert_id: int) -> bool:
    """Delete an alert."""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == user_id
    ).first()

    if not alert:
        return False

    db.delete(alert)
    db.commit()
    return True


def check_alerts(db: Session) -> List[dict]:
    """
    Check all active alerts against current prices.
    Called by the scheduler every few minutes.
    Returns list of triggered alerts.
    """
    active_alerts = db.query(Alert).filter(
        Alert.is_active == True,
        Alert.is_triggered == False
    ).all()

    triggered = []

    for alert in active_alerts:
        try:
            # Fetch current price based on asset type
            if alert.asset_type == "stock":
                data = fetch_stock(alert.symbol)
                current_price = data.get("current_price", 0)
            elif alert.asset_type == "crypto":
                data = fetch_crypto(alert.symbol)
                current_price = data.get("current_price", 0)
            else:
                continue

            # Update current price on alert
            alert.current_price = current_price

            # Check if condition is met
            condition_met = (
                alert.condition == "above" and current_price >= alert.target_price
            ) or (
                alert.condition == "below" and current_price <= alert.target_price
            )

            if condition_met:
                alert.is_triggered = True
                alert.triggered_at = datetime.utcnow()
                triggered.append({
                    "symbol": alert.symbol,
                    "condition": alert.condition,
                    "target_price": alert.target_price,
                    "current_price": current_price,
                    "triggered_at": str(alert.triggered_at)
                })

            db.commit()

        except Exception as e:
            continue

    return triggered