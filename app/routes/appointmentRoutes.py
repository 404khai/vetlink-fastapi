from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, date, time

from app import models, schemas, database
from app.utils.authUtils import get_current_user

router = APIRouter(prefix="/appointments", tags=["Appointments"])

# Dependency to get DB session
def getDb():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------------------------------------
# Create a new appointment (Pet Owner → Vet)
# -----------------------------------------------------------
@router.post("/new", response_model=schemas.AppointmentResponse)
def create_appointment(
    appointment: schemas.AppointmentCreate,
    db: Session = Depends(getDb),
    current_user=Depends(get_current_user),
):
    # ✅ Only pet owners can book appointments
    if current_user.role != "pet_owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only pet owners can create appointments",
        )

    # ✅ Get Pet Owner Profile
    pet_owner = db.query(models.PetOwner).filter(models.PetOwner.userId == current_user.id).first()
    if not pet_owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PetOwner profile not found"
        )

    # ✅ Validate Vet Exists
    vet = db.query(models.Vet).filter(models.Vet.id == appointment.vetId).first()
    if not vet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vet not found")

    # ✅ Validate Pet Belongs to Owner
    pet = (
        db.query(models.Pet)
        .filter(models.Pet.id == appointment.petId, models.Pet.ownerId == pet_owner.id)
        .first()
    )
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This pet does not belong to you",
        )

    # ✅ Validate that scheduled time is in the future
    now = datetime.utcnow().date()
    if appointment.scheduledDate < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot schedule an appointment in the past",
        )

    # ✅ Create appointment
    new_appointment = models.Appointment(
        petOwnerId=pet_owner.id,
        vetId=appointment.vetId,
        petId=appointment.petId,
        scheduledDate=appointment.scheduledDate,
        scheduledTime=appointment.scheduledTime,
        appointmentType=appointment.appointmentType,
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment


# -----------------------------------------------------------
# Get all appointments for the current user
# -----------------------------------------------------------
@router.get("/get_appointments", response_model=list[schemas.AppointmentResponse])
def get_my_appointments(
    db: Session = Depends(getDb), current_user=Depends(get_current_user)
):
    if current_user.role == "pet_owner":
        pet_owner = db.query(models.PetOwner).filter(models.PetOwner.userId == current_user.id).first()
        if not pet_owner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PetOwner not found")
        appointments = db.query(models.Appointment).filter(models.Appointment.petOwnerId == pet_owner.id).all()
    elif current_user.role == "vet":
        vet = db.query(models.Vet).filter(models.Vet.userId == current_user.id).first()
        if not vet:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vet not found")
        appointments = db.query(models.Appointment).filter(models.Appointment.vetId == vet.id).all()
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return appointments


# -----------------------------------------------------------
# Update appointment status (Vet only)
# -----------------------------------------------------------
@router.patch("/{appointment_id}/status")
def update_appointment_status(
    appointment_id: int,
    status_update: schemas.AppointmentStatus,
    db: Session = Depends(getDb),
    current_user=Depends(get_current_user),
):
    if current_user.role != "vet":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vets can update appointment status",
        )

    vet = db.query(models.Vet).filter(models.Vet.userId == current_user.id).first()
    if not vet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vet not found")

    appointment = (
        db.query(models.Appointment)
        .filter(models.Appointment.id == appointment_id, models.Appointment.vetId == vet.id)
        .first()
    )

    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

    appointment.status = status_update
    db.commit()
    db.refresh(appointment)
    return {"message": f"Appointment marked as {appointment.status}"}


# -----------------------------------------------------------
# Delete appointment (Pet Owner only)
# -----------------------------------------------------------
@router.delete("/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(getDb),
    current_user=Depends(get_current_user),
):
    if current_user.role != "pet_owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only pet owners can delete appointments",
        )

    pet_owner = db.query(models.PetOwner).filter(models.PetOwner.userId == current_user.id).first()
    if not pet_owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PetOwner not found")

    appointment = (
        db.query(models.Appointment)
        .filter(models.Appointment.id == appointment_id, models.Appointment.petOwnerId == pet_owner.id)
        .first()
    )

    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

    db.delete(appointment)
    db.commit()
    return {"message": "Appointment deleted successfully"}
