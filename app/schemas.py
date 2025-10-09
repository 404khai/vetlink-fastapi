from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from .enums import UserRole, AppointmentStatus

# =====================================================
# USER SCHEMAS
# =====================================================
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserInfo(BaseModel):
    id: int
    email: str
    role: str
    name: str | None = None
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserInfo
    
class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserRequest(UserBase):
    name: Optional[str] = None
    email: EmailStr
    password: Optional[str] = None  # Optional to allow Google OAuth users
    googleId: Optional[str] = None
    role: UserRole = UserRole.PET_OWNER


class UserResponse(UserBase):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    createdAt: datetime
    petOwnerProfile: Optional["PetOwnerResponse"] = None
    vetProfile: Optional["VetResponse"] = None

    class Config:
        orm_mode = True


# =====================================================
# PET SCHEMAS
# =====================================================

class PetBase(BaseModel):
    name: str
    type: str
    age: Optional[int]
    breed: Optional[str]
    weight: Optional[str]


class PetRequest(PetBase):
    pass


class PetResponse(PetBase):
    id: int
    ownerId: int

    class Config:
        orm_mode = True


# =====================================================
# PET OWNER SCHEMAS
# =====================================================

class PetOwnerBase(BaseModel):
    userId: int


class PetOwnerRequest(PetOwnerBase):
    petId: int


class PetOwnerResponse(PetOwnerBase):
    id: int
    user: UserResponse
    pets: List[PetResponse] = []

    class Config:
        orm_mode = True


# =====================================================
# VET SCHEMAS
# =====================================================

class VetBase(BaseModel):
    userId: int
    specialization: Optional[str] = None
    bio: Optional[str] = None


class VetRequest(VetBase):
    pass


class VetResponse(VetBase):
    id: int
    user: UserResponse

    class Config:
        orm_mode = True


# =====================================================
# APPOINTMENT SCHEMAS
# =====================================================

class AppointmentBase(BaseModel):
    scheduledFor: datetime
    status: Optional[AppointmentStatus] = AppointmentStatus.PENDING


class AppointmentRequest(AppointmentBase):
    petOwnerId: int
    vetId: int


class AppointmentResponse(AppointmentBase):
    id: int
    createdAt: datetime
    petOwner: Optional[PetOwnerResponse] = None
    vet: Optional[VetResponse] = None

    class Config:
        orm_mode = True
