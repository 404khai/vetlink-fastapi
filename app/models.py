from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
from enums import UserRole, AppointmentStatus


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=True)  # Optional for Google users
    googleId = Column(String, unique=True, nullable=True)

    role = Column(Enum(UserRole), nullable=False, default=UserRole.PET_OWNER)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)

    # relationships
    petOwnerProfile = relationship("PetOwner", uselist=False, back_populates="user")
    vetProfile = relationship("Vet", uselist=False, back_populates="user")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")


class PetOwner(Base):
    __tablename__ = "petOwners"

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    user = relationship("User", back_populates="petOwnerProfile")
    pets = relationship("Pet", back_populates="owner", cascade="all, delete-orphan")
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
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    age = Column(Integer, nullable=True)
    breed = Column(String, nullable=True)
    weight = Column(String, nullable=True)
    ownerId = Column(Integer, ForeignKey("pet_owners.id", ondelete="CASCADE"))

    owner = relationship("PetOwner", back_populates="pets")
    appointments = relationship("Appointment", back_populates="pet", cascade="all, delete-orphan")


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    scheduledFor = Column(DateTime, nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDING)

    petOwnerId = Column(Integer, ForeignKey("pet_owners.id", ondelete="CASCADE"))
    vetId = Column(Integer, ForeignKey("vets.id", ondelete="CASCADE"))
    petId = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"))

    petOwner = relationship("PetOwner", back_populates="appointments")
    vet = relationship("Vet", back_populates="appointments")
    pet = relationship("Pet", back_populates="appointments")
    comments = relationship("Comment", back_populates="appointment", cascade="all, delete-orphan")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDING)

    petOwnerId = Column(Integer, ForeignKey("pet_owners.id", ondelete="CASCADE"))
    vetId = Column(Integer, ForeignKey("vets.id", ondelete="CASCADE"))
    petId = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"))

    petOwner = relationship("PetOwner", back_populates="bookings")
    vet = relationship("Vet", back_populates="bookings")
    pet = relationship("Pet", back_populates="bookings")
