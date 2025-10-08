from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas, database
from app.utils.auth import hashPassword
from enums import UserRole

router = APIRouter(prefix="/users", tags=["Users"])

def getDb():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/new", response_model=schemas.UserResponse)
def createUser(user: schemas.UserRequest, db: Session = Depends(getDb)):
    existingUser = db.query(models.User).filter(models.User.email == user.email).first()
    if existingUser:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashedPw = hashPassword(user.password) if user.password else None
    newUser = models.User(
        name=user.name,
        email=user.email,
        password=hashedPw,
        role=user.role,
    )

    db.add(newUser)
    db.commit()
    db.refresh(newUser)

    # Create role-specific profile
    if user.role == UserRole.PET_OWNER:
        petOwnerProfile = models.PetOwner(userId=newUser.id)
        db.add(petOwnerProfile)
    elif user.role == UserRole.VET:
        vetProfile = models.Vet(userId=newUser.id)
        db.add(vetProfile)

    db.commit()
    db.refresh(newUser)

    return newUser

@router.delete("/{userId}")
def delete_user(userId: int, db: Session = Depends(getDb)):
    user = db.query(models.Users).filter(models.Users.id == userId).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
