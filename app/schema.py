from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# ----- USER
class UserRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True