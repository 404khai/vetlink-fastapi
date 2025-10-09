from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app import database, models
import os

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------

# Secret key for signing JWTs (store securely in .env for production)
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")  # fallback for local dev
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# OAuth2 scheme for extracting "Authorization: Bearer <token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ------------------------------------------------------------------
# JWT Token Creation
# ------------------------------------------------------------------

def createAccessToken(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ------------------------------------------------------------------
# Token Verification
# ------------------------------------------------------------------

def verifyAccessToken(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception


# ------------------------------------------------------------------
# Get Current User (Dependency)
# ------------------------------------------------------------------

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.getDb)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = verifyAccessToken(token, credentials_exception)
    user_id = int(payload.get("sub"))

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise credentials_exception

    return user
