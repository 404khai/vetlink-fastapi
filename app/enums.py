from enum import Enum as PyEnum

class UserRole(PyEnum):
    PET_OWNER = "pet_owner"
    VET = "vet"
    ADMIN = "admin"


class AppointmentStatus(PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    RESCHEDULED = "rescheduled"