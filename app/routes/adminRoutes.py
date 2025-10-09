from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import database
from app.models import User, UserRole, PetOwner, Vet

router = APIRouter(prefix="/admin", tags=["Admin"])

def getDb():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.put("/convert_to_vet/{user_id}")
def convert_to_vet(user_id: int, db: Session = Depends(getDb)):
    # 1️⃣ Find the user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2️⃣ Ensure they are currently a Pet Owner
    if user.role != UserRole.PET_OWNER:
        raise HTTPException(status_code=400, detail="User is not a pet owner")

    # 3️⃣ Delete their PetOwnerProfile if it exists
    pet_owner = db.query(PetOwner).filter(PetOwner.user_id == user_id).first()
    if pet_owner:
        db.delete(pet_owner)

    # 4️⃣ Create a new Vet profile
    new_vet = Vet(user_id=user_id)
    db.add(new_vet)

    # 5️⃣ Update role
    user.role = UserRole.VET

    # 6️⃣ Save changes
    db.commit()
    db.refresh(user)

    return {"message": "User converted to Vet successfully", "user": user}
