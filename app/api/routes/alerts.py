from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.alert import AlertCreate, AlertResponse
from app.services.alert_service import get_alerts, create_alert, delete_alert, check_alerts
from typing import List

router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"]
)

TEMP_USER_ID = 1


@router.get("/")
def read_alerts(db: Session = Depends(get_db)):
    """Get all price alerts for the user."""
    alerts = get_alerts(db, TEMP_USER_ID)
    return {"alerts": alerts, "count": len(alerts)}


@router.post("/")
def add_alert(data: AlertCreate, db: Session = Depends(get_db)):
    """
    Create a new price alert.
    Body: { symbol, asset_type, condition, target_price }
    condition must be 'above' or 'below'
    """
    try:
        alert = create_alert(db, TEMP_USER_ID, data)
        return {"message": "Alert created", "alert": alert}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{alert_id}")
def remove_alert(alert_id: int, db: Session = Depends(get_db)):
    """Delete a price alert."""
    success = delete_alert(db, TEMP_USER_ID, alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert deleted"}


@router.get("/check")
def trigger_alert_check(db: Session = Depends(get_db)):
    """
    Manually trigger an alert check against live prices.
    In production this runs automatically via the scheduler.
    """
    triggered = check_alerts(db)
    return {
        "triggered_count": len(triggered),
        "triggered_alerts": triggered
    }