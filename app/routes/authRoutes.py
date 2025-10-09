from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests
from app import models, database, schemas
from app.utils.auth import verifyPassword, createAccessToken, hashPassword
from app.enums import UserRole
import os
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Auth"])

def getDb():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


@router.post("/register")
def createUser(user: schemas.UserRequest, db: Session = Depends(getDb)):
    existingUser = db.query(models.User).filter(models.User.email == user.email).first()
    if existingUser:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashedPw = hashPassword(user.password) if user.password else None

    newUser = models.User(
        name=user.name,
        email=user.email,
        password=hashedPw,
        googleId=user.googleId,
        role=user.role,
    )

    db.add(newUser)
    db.commit()
    db.refresh(newUser)

    # Role profile creation
    if user.role == UserRole.PET_OWNER:
        db.add(models.PetOwner(userId=newUser.id))
    elif user.role == UserRole.VET:
        db.add(models.Vet(userId=newUser.id))
    db.commit()

    # Generate JWT
    token = createAccessToken({"sub": str(newUser.id), "email": newUser.email})

    return {"access_token": token, "user": newUser}


# @router.post("/google")
# def googleLogin(token: str = Body(...), role: UserRole = Body(UserRole.PET_OWNER), db: Session = Depends(getDb)):
#     try:
#         id_info = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
#         email = id_info.get("email")
#         name = id_info.get("name")
#         google_id = id_info.get("sub")
#     except Exception:
#         raise HTTPException(status_code=400, detail="Invalid Google token")

#     # Check if user exists
#     user = db.query(models.User).filter(models.User.email == email).first()

#     if not user:
#         user = models.User(
#             name=name,
#             email=email,
#             googleId=google_id,
#             role=role  # 👈 use the role passed from frontend
#         )
#         db.add(user)
#         db.commit()
#         db.refresh(user)

#         # Create profile dynamically
#         if role == UserRole.VET:
#             db.add(models.Vet(userId=user.id))
#         else:
#             db.add(models.PetOwner(userId=user.id))
#         db.commit()

#     access_token = createAccessToken({"sub": str(user.id), "email": user.email})
#     return {"access_token": access_token, "token_type": "bearer", "user": user}



@router.post("/login", response_model=schemas.TokenResponse)
def login_user(request: schemas.LoginRequest, db: Session = Depends(getDb)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not user.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account was created using Google Sign-In. Please use Google to sign in."
        )

    if not verifyPassword(request.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Generate JWT
    access_token_expires = timedelta(minutes=60)
    access_token = createAccessToken(
        data={"sub": str(user.id), "email": user.email, "role": user.role.value},
        expires_delta=access_token_expires
    )

    # ✅ Return both token and user info
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role.value,
            "name": user.name
        }
    }
