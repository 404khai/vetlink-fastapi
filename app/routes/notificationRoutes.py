from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app import models, database, schemas
from app.utils.authUtils import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])

def getDb():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Get all notifications for current user
@router.get("/getAll", response_model=List[schemas.NotificationResponse])
def get_notifications(db: Session = Depends(getDb), current_user=Depends(get_current_user)):
    return db.query(models.Notification).filter(models.Notification.user_id == current_user.id).order_by(models.Notification.created_at.desc()).all()


# ✅ Mark a notification as read
@router.patch("/{notification_id}/read", response_model=schemas.NotificationResponse)
def mark_as_read(notification_id: int, db: Session = Depends(getDb), current_user=Depends(get_current_user)):
    notif = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.user_id == current_user.id
    ).first()

    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    notif.is_read = True
    db.commit()
    db.refresh(notif)
    return notif


# ✅ Delete a notification
@router.delete("/{notification_id}")
def delete_notification(notification_id: int, db: Session = Depends(getDb), current_user=Depends(get_current_user)):
    notif = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.user_id == current_user.id
    ).first()

    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    db.delete(notif)
    db.commit()
    return {"message": "Notification deleted"}
