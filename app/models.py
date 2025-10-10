from sqlalchemy import Column, Float, Integer, String, ForeignKey, DateTime, Enum, Date, Time, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from app.enums import AppointmentType, UserRole, AppointmentStatus, NotificationType

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=True)
    googleId = Column(String, unique=True, nullable=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.PET_OWNER)
    imageUrl = Column(String, nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)

    notifications = relationship("Notification", uselist=False, back_populates="user")
    petOwnerProfile = relationship("PetOwner", uselist=False, back_populates="user")
    vetProfile = relationship("Vet", uselist=False, back_populates="user")
    

class PetOwner(Base):
    __tablename__ = "pet_owners"

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
    species = Column(String, nullable=False)  # e.g., Dog, Cat, Bird (instead of generic 'type')
    breed = Column(String, nullable=False)
    gender = Column(String, nullable=False)  # "Male" / "Female"
    age = Column(String, nullable=False)
    weight = Column(Float, nullable=True)  # numeric type for better operations
    color = Column(String, nullable=False)
    microchip_number = Column(String, unique=True, nullable=True)
    vaccination_status = Column(String, nullable=True)  # e.g. "Up-to-date", "Pending"
    imageUrl = Column(String, nullable=True)
    # medical_notes = Column(Text, nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)

    ownerId = Column(Integer, ForeignKey("pet_owners.id", ondelete="CASCADE"))
    owner = relationship("PetOwner", back_populates="pets")

    appointments = relationship("Appointment", back_populates="pet", cascade="all, delete-orphan")



class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)

    # ✅ Split scheduledFor into separate fields
    scheduledDate = Column(Date, nullable=False)
    scheduledTime = Column(Time, nullable=False)

    # ✅ New Enum field for appointment type
    appointmentType = Column(Enum(AppointmentType), nullable=False)

    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDING, nullable=False)
    

    # ✅ Relationships
    petOwnerId = Column(Integer, ForeignKey("pet_owners.id", ondelete="CASCADE"))
    vetId = Column(Integer, ForeignKey("vets.id", ondelete="CASCADE"))
    petId = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"))

    petOwner = relationship("PetOwner", back_populates="appointments")
    vet = relationship("Vet", back_populates="appointments")
    pet = relationship("Pet", back_populates="appointments")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # relationships
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="notifications")