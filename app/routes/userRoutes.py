from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, database
from app.utils.auth import hashPassword
from app.enums import UserRole

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

    # Validate either password or googleId is provided
    if not user.password and not user.googleId:
        raise HTTPException(status_code=400, detail="Password or Google ID required")

    hashed_pw = hashPassword(user.password) if user.password else None

    newUser = models.User(
        name=user.name,
        email=user.email,
        password=hashed_pw,
        googleId=user.googleId,
        role=user.role,
    )
    db.add(newUser)
    db.commit()
    db.refresh(newUser)

    # Role-specific profile
    if user.role == UserRole.PET_OWNER:
        db.add(models.PetOwner(userId=newUser.id))
    elif user.role == UserRole.VET:
        db.add(models.Vet(userId=newUser.id))

    db.commit()
    db.refresh(newUser)
    return newUser
