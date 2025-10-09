from enum import Enum

class UserRole(str, Enum):
    PET_OWNER = "pet_owner"
    VET = "vet"
    ADMIN = "admin"


class AppointmentType(str, Enum):
    CHECKUP = "Checkup"
    VACCINATION = "Vaccination"
    GROOMING = "Grooming"
    SURGERY = "Surgery"
    EMERGENCY_CARE = "Emergency Care"
    TREATMENT = "Treatment"
    CONSULTATION = "Consultation"


class AppointmentStatus(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    RESCHEDULED = "Rescheduled"
    CANCELLED = "Cancelled"