from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

from .database import Base
from enums import UserRole, AppointmentStatus



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

    # Optional for Google OAuth users
    password = Column(String, nullable=True)
    googleId = Column(String, unique=True, nullable=True)

    role = Column(Enum(UserRole), nullable=False, default=UserRole.PET_OWNER)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)

    # relationships (depending on role)
    petOwnerProfile = relationship("PetOwner", uselist=False, back_populates="user")
    vetProfile = relationship("Vet", uselist=False, back_populates="user")


class PetOwner(Base):
    __tablename__ = "petOwners"

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    petId = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"))

    user = relationship("User", back_populates="petOwnerProfile")
    appointments = relationship("Appointment", back_populates="petOwner", cascade="all, delete-orphan")


class Vet(Base):
    __tablename__ = "vets"

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    specialization = Column(String, nullable=True)
    bio = Column(String, nullable=True)

    user = relationship("User", back_populates="vetProfile")
    appointments = relationship("Appointment", back_populates="vet", cascade="all, delete-orphan")


class Pet(Base):
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    petName = Column(String, nullable=False)
    petType = Column(String, nullable=False)

    user = relationship("User", back_populates="petOwnerProfile")
    appointments = relationship("Appointment", back_populates="petOwner", cascade="all, delete-orphan")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    scheduledFor = Column(DateTime, nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDING)

    petOwnerId = Column(Integer, ForeignKey("petOwners.id", ondelete="CASCADE"))
    vetId = Column(Enum(AppointmentStatus), ForeignKey("vets.id", ondelete="CASCADE"))

    petOwner = relationship("PetOwner", back_populates="appointments")
    vet = relationship("Vet", back_populates="appointments")

