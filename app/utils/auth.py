from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

# bcrypt context
pwdContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

# secret key & algorithm
SECRET_KEY = "your_super_secret_key_here"  # ⚠️ ideally use env vars
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour


# ---- PASSWORD HASHING ----
def hashPassword(password: str) -> str:
    return pwdContext.hash(password)


def verifyPassword(plainPassword: str, hashedPassword: str) -> bool:
    return pwdContext.verify(plainPassword, hashedPassword)


# ---- JWT TOKEN CREATION ----
def createAccessToken(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decodeAccessToken(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
