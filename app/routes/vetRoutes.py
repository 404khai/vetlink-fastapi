from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from app import models, schemas, database
from app.enums import AppointmentStatus
from app.utils.authUtils import get_current_user

router = APIRouter(
    prefix="/vets",
    tags=["Vets"]
)

def getDb():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/pets", response_model=List[schemas.PetResponse])
def get_pets_from_upcoming_appointments(
    db: Session = Depends(getDb),
    current_user=Depends(get_current_user)
):
    if current_user.role != "vet":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only vets can view this")

    vet = db.query(models.Vet).filter(models.Vet.userId == current_user.id).first()
    if not vet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vet profile not found")

    today = datetime.utcnow().date()

    appointments = (
        db.query(models.Appointment)
        .filter(
            models.Appointment.vetId == vet.id,
            models.Appointment.status == AppointmentStatus.ACCEPTED,
            models.Appointment.scheduledDate >= today,
        )
        .all()
    )

    # Extract pets from appointments
    pets = [appt.pet for appt in appointments if appt.pet is not None]

    # Remove duplicates if a pet appears in multiple appointments
    unique_pets = list({pet.id: pet for pet in pets}.values())

    return unique_pets
