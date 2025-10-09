from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, date, time
from .enums import UserRole, AppointmentStatus, AppointmentType

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
    imageUrl: Optional[str] = None


class UserResponse(UserBase):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    createdAt: datetime
    imageUrl: Optional[str] = None
    petOwnerProfile: Optional["PetOwnerResponse"] = None
    vetProfile: Optional["VetResponse"] = None

    class Config:
        orm_mode = True


class SimpleUserResponse(BaseModel):
    id: int
    name: Optional[str]
    email: EmailStr
    imageUrl: Optional[str] = None

    class Config:
        orm_mode = True

# =====================================================
# PET SCHEMAS
# =====================================================

class PetRequest(BaseModel):
    name: str
    species: str
    breed: str
    gender: str
    age: str
    weight: Optional[float]
    color: str
    microchip_number: Optional[str]
    vaccination_status: Optional[str]
    imageUrl: Optional[str] = None


class PetResponse(BaseModel):
    id: int
    ownerId: int
    name: str
    species: str
    breed: str
    gender: str
    age: str
    weight: Optional[float]
    color: str
    microchip_number: Optional[str]
    vaccination_status: Optional[str]
    imageUrl: Optional[str] = None

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
    user: SimpleUserResponse
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
    user: SimpleUserResponse

    class Config:
        orm_mode = True



# =====================================================
# APPOINTMENT SCHEMAS
# =====================================================

class AppointmentBase(BaseModel):
    scheduledDate: date
    scheduledTime: time
    appointmentType: AppointmentType
    petId: int
    vetId: int

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentResponse(AppointmentBase):
    id: int
    status: AppointmentStatus

    class Config:
        orm_mode = True