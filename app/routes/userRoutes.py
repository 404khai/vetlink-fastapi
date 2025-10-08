from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, database


router = APIRouter(prefix="/users", tags=["Users"])


# Dependency for DB session
def getDb():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/new", response_model=schemas.UserResponse)
def createUser(user: schemas.UserRequest, db: Session = Depends(getDb)):
    dbUser = db.query(models.User).filter(models.User.email == user.email).first()
    if dbUser:
        raise HTTPException(status_code=400, detail="Email already registered")

    newUser = models.Users(name=user.name, email=user.email, password=user.password)
    db.add(newUser)
    db.commit()
    db.refresh(newUser)
    return newUser


@router.get("/all", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(getDb)):
    return db.query(models.Users).all()


#Get a specific user
@router.get("/{userId}", response_model=schemas.UserResponse)
def get_user(userId: int, db: Session = Depends(getDb)):
    user = db.query(models.Users).filter(models.Users.id == userId).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{userId}")
def delete_user(userId: int, db: Session = Depends(getDb)):
    user = db.query(models.Users).filter(models.Users.id == userId).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
