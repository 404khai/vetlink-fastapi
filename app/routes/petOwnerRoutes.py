from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app import models, database, schemas
from app.utils.authUtils import get_current_user
from app.utils.cloudinaryUtils import upload_image
from typing import Optional

router = APIRouter(prefix="/petowners", tags=["Pet Owners"])

def getDb():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/add_pet", response_model=schemas.PetResponse)
def add_pet_for_owner(
    name: str = Form(...),
    species: str = Form(...),
    breed: str = Form(...),
    gender: str = Form(...),
    age: str = Form(...),
    color: str = Form(...),
    weight: Optional[float] = Form(None),
    microchip_number: Optional[str] = Form(None),
    vaccination_status: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(getDb),
    current_user=Depends(get_current_user)
):
    if current_user.role != "pet_owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only pet owners can add pets")

    pet_owner = db.query(models.PetOwner).filter(models.PetOwner.userId == current_user.id).first()
    if not pet_owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PetOwner profile not found")

    # Upload to Cloudinary if file exists
    image_url = upload_image(image.file) if image else None

    new_pet = models.Pet(
        name=name,
        species=species,
        breed=breed,
        gender=gender,
        age=age,
        weight=weight,
        color=color,
        microchip_number=microchip_number,
        vaccination_status=vaccination_status,
        ownerId=pet_owner.id,
        imageUrl=image_url
    )

    db.add(new_pet)
    db.commit()
    db.refresh(new_pet)

    return new_pet



# -----------------------------------------------------------
# Get all pets for the current pet owner
# -----------------------------------------------------------
@router.get("/pets", response_model=list[schemas.PetResponse])
def get_my_pets(db: Session = Depends(getDb), current_user=Depends(get_current_user)):
    if current_user.role != "pet_owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only pet owners can view pets")

    pet_owner = db.query(models.PetOwner).filter(models.PetOwner.userId == current_user.id).first()
    if not pet_owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PetOwner profile not found")

    return pet_owner.pets


@router.get("/get_vets", response_model=list[schemas.VetResponse])
def get_vets(db: Session = Depends(getDb), current_user=Depends(get_current_user)):
    if current_user.role != "pet_owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only pet owners can view all vets")
    pet_owner = db.query(models.PetOwner).filter(models.PetOwner.userId == current_user.id).first()
    vets = db.query(models.Vet).all()
    if not pet_owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PetOwner profile not found")

    return vets
# -----------------------------------------------------------
# Delete a pet
# -----------------------------------------------------------
@router.delete("/pets/{pet_id}")
def delete_pet(pet_id: int, db: Session = Depends(getDb), current_user=Depends(get_current_user)):
    pet = db.query(models.Pet).join(models.PetOwner).filter(
        models.Pet.id == pet_id,
        models.PetOwner.userId == current_user.id
    ).first()

    if not pet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pet not found or not owned by you")

    db.delete(pet)
    db.commit()
    return {"message": "Pet deleted successfully"}
