from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from app import models, schemas, database
from app.enums import AppointmentStatus
from app.utils.authUtils import get_current_user

router = APIRouter(prefix="/appointments", tags=["Appointments"])

def getDb():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------------------------------------
# Create a new appointment
# -----------------------------------------------------------
@router.post("/new", response_model=schemas.AppointmentResponse)
def create_appointment(
    appointment: schemas.AppointmentCreate,
    db: Session = Depends(getDb),
    current_user=Depends(get_current_user),
):
    if current_user.role != "pet_owner":
        raise HTTPException(status_code=403, detail="Only pet owners can create appointments")

    pet_owner = db.query(models.PetOwner).filter(models.PetOwner.userId == current_user.id).first()
    if not pet_owner:
        raise HTTPException(status_code=404, detail="PetOwner profile not found")

    vet = db.query(models.Vet).filter(models.Vet.id == appointment.vetId).first()
    if not vet:
        raise HTTPException(status_code=404, detail="Vet not found")

    pet = db.query(models.Pet).filter(
        models.Pet.id == appointment.petId,
        models.Pet.ownerId == pet_owner.id
    ).first()
    if not pet:
        raise HTTPException(status_code=403, detail="This pet does not belong to you")

    if appointment.scheduledDate < datetime.utcnow().date():
        raise HTTPException(status_code=400, detail="Cannot schedule an appointment in the past")

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
# Get all appointments for the current user (with relationships)
# -----------------------------------------------------------
@router.get("/get_appointments", response_model=list[schemas.AppointmentResponse])
def get_my_appointments(
    db: Session = Depends(getDb), current_user=Depends(get_current_user)
):
    if current_user.role == "pet_owner":
        pet_owner = db.query(models.PetOwner).filter(models.PetOwner.userId == current_user.id).first()
        if not pet_owner:
            raise HTTPException(status_code=404, detail="PetOwner not found")

        appointments = (
            db.query(models.Appointment)
            .options(
                joinedload(models.Appointment.petOwner).joinedload(models.PetOwner.user),
                joinedload(models.Appointment.vet).joinedload(models.Vet.user),
                joinedload(models.Appointment.pet),
            )
            .filter(models.Appointment.petOwnerId == pet_owner.id)
            .all()
        )

    elif current_user.role == "vet":
        vet = db.query(models.Vet).filter(models.Vet.userId == current_user.id).first()
        if not vet:
            raise HTTPException(status_code=404, detail="Vet not found")

        appointments = (
            db.query(models.Appointment)
            .options(
                joinedload(models.Appointment.petOwner).joinedload(models.PetOwner.user),
                joinedload(models.Appointment.vet).joinedload(models.Vet.user),
                joinedload(models.Appointment.pet),
            )
            .filter(models.Appointment.vetId == vet.id)
            .all()
        )

    else:
        raise HTTPException(status_code=403, detail="Access denied")

    return appointments



@router.get("/upcoming", response_model=list[schemas.AppointmentResponse])
def get_upcoming_appointments_for_vet(
    db: Session = Depends(getDb),
    current_user=Depends(get_current_user)
):
    if current_user.role != "vet":
        raise HTTPException(status_code=403, detail="Only vets can view upcoming appointments")

    vet = db.query(models.Vet).filter(models.Vet.userId == current_user.id).first()
    if not vet:
        raise HTTPException(status_code=404, detail="Vet not found")

    today = datetime.utcnow().date()

    appointments = (
        db.query(models.Appointment)
        .filter(
            models.Appointment.vetId == vet.id,
            models.Appointment.status == AppointmentStatus.ACCEPTED,
            models.Appointment.scheduledDate >= today,
        )
        .order_by(models.Appointment.scheduledDate.asc())
        .all()
    )

    return appointments

# -----------------------------------------------------------
# Update appointment status (Vet only)
# -----------------------------------------------------------
@router.patch("/{appointment_id}/status")
def update_appointment_status(
    appointment_id: int,
    status_update: schemas.StatusUpdate,
    db: Session = Depends(getDb),
    current_user=Depends(get_current_user),
):
    if current_user.role != "vet":
        raise HTTPException(status_code=403, detail="Only vets can update appointment status")

    vet = db.query(models.Vet).filter(models.Vet.userId == current_user.id).first()
    if not vet:
        raise HTTPException(status_code=404, detail="Vet not found")

    appointment = (
        db.query(models.Appointment)
        .filter(models.Appointment.id == appointment_id, models.Appointment.vetId == vet.id)
        .first()
    )
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    from app.enums import AppointmentStatus
    try:
        appointment.status = AppointmentStatus[status_update.status.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid status value")

    db.commit()
    db.refresh(appointment)
    return {"message": f"Appointment marked as {appointment.status.value}"}





@router.patch("/{appointment_id}/reschedule", response_model=schemas.AppointmentResponse)
def reschedule_appointment(appointment_id: int, update: schemas.AppointmentReschedule, db: Session = Depends(getDb), current_user=Depends(get_current_user)):
    if current_user.role != "vet":
        raise HTTPException(status_code=403, detail="Only vets can reschedule appointments")

    vet = db.query(models.Vet).filter(models.Vet.userId == current_user.id).first()
    if not vet:
        raise HTTPException(status_code=404, detail="Vet not found")

    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id, models.Appointment.vetId == vet.id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointment.scheduledDate = update.scheduledDate
    appointment.scheduledTime = update.scheduledTime
    appointment.status = AppointmentStatus.RESCHEDULED
    db.commit()
    db.refresh(appointment)
    return appointment

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
