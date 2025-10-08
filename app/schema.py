from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from enums import UserRole, AppointmentStatus

# =====================================================
# USER SCHEMAS
# =====================================================

class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: Optional[str] = None  # Optional to allow Google OAuth users
    googleId: Optional[str] = None
    role: UserRole = UserRole.PET_OWNER


class UserResponse(UserBase):
    id: int
    role: UserRole
    createdAt: datetime

    class Config:
        orm_mode = True


# =====================================================
# PET SCHEMAS
# =====================================================

class PetBase(BaseModel):
    petName: str
    petType: str


class PetCreate(PetBase):
    pass


class PetResponse(PetBase):
    id: int
    userId: int

    class Config:
        orm_mode = True


# =====================================================
# PET OWNER SCHEMAS
# =====================================================

class PetOwnerBase(BaseModel):
    userId: int


class PetOwnerCreate(PetOwnerBase):
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


class VetCreate(VetBase):
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


class AppointmentCreate(AppointmentBase):
    petOwnerId: int
    vetId: int


class AppointmentResponse(AppointmentBase):
    id: int
    createdAt: datetime
    petOwner: Optional[PetOwnerResponse] = None
    vet: Optional[VetResponse] = None

    class Config:
        orm_mode = True
