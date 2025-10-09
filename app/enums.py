from enum import Enum

class UserRole(str, Enum):
    PET_OWNER = "pet_owner"
    VET = "vet"
    ADMIN = "admin"


class AppointmentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    RESCHEDULED = "rescheduled"