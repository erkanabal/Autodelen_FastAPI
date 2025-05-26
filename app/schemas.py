from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum

# ====================
# ENUMS
# ====================

class PublicUserRoleEnum(str, Enum):
    owner = "owner"
    renter = "renter"
    passenger = "passenger"

class UserRoleEnum(str, Enum):
    owner = "owner"
    renter = "renter"
    passenger = "passenger"
    admin = "admin"

# ====================
# USER SCHEMAS
# ====================

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: PublicUserRoleEnum  # admin bu enumda yok

    class Config:
        use_enum_values = False

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRoleEnum

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

# ====================
# TOKEN SCHEMAS
# ====================

class Token(BaseModel):
    access_token: str
    token_type: str

# ====================
# VEHICLE SCHEMAS
# ====================

class VehicleBase(BaseModel):
    brand: str
    model: str
    license_plate: str
    seats: int
    luggage: Optional[int] = None

class VehicleCreate(VehicleBase):
    pass

class VehicleOut(VehicleBase):
    id: int
    owner_id: int
    available: bool

    class Config:
        from_attributes = True

# ====================
# RENTAL SCHEMAS
# ====================

class RentalBase(BaseModel):
    vehicle_id: int
    start_date: datetime
    end_date: datetime
    total_price: Optional[float] = None  # float olmalı, int değil

class RentalCreate(RentalBase):
    pass

class RentalOut(RentalBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# ====================
# RIDE SCHEMAS
# ====================

class RideBase(BaseModel):
    start_date: datetime
    end_date: datetime
    start_location: str
    end_location: str
    available_seats: int

class RideCreate(RideBase):
    rental_id: int

class RideOut(RideBase):
    id: int
    rental_id: int
    renter_id: int

    class Config:
        from_attributes = True

# ====================
# RIDE PARTICIPANT SCHEMAS
# ====================

class RideParticipantBase(BaseModel):
    ride_id: int
    passengers_count: int = Field(default=1, ge=1)

class RideParticipantCreate(RideParticipantBase):
    pass

class RideParticipantOut(RideParticipantBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# ====================
# REVIEW SCHEMAS
# ====================

class ReviewType(str, Enum):
    vehicle = "vehicle"
    ride = "ride"
    renter = "renter"

class ReviewBase(BaseModel):
    type: ReviewType
    rating: int = Field(..., ge=0, le=10)
    rating_category: str
    comment: Optional[str] = None
    vehicle_id: Optional[int] = None
    ride_id: Optional[int] = None
    renter_id: Optional[int] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=0, le=10)
    comment: Optional[str] = None

class ReviewOut(ReviewBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
