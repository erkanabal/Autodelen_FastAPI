from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum

# ====================
# ENUMS
# ====================

# 🎯 Swagger'da sadece owner, renter, passenger görünsün
class PublicUserRoleEnum(str, Enum):
    owner = "owner"
    renter = "renter"
    passenger = "passenger"

# 🎯 Veritabanı için tam enum (admin dahil)
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
        use_enum_values = False  # Etiketler görünsün (Swagger)

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRoleEnum

    class Config:
        from_attributes = True  # Pydantic v2 desteği

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

# ====================
# TOKEN
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
    total_price: Optional[int] = None  

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
    start_location: str
    end_location: str
    start_date: datetime
    end_date: datetime
    available_seats: int
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
    rental = "rental"
    ride = "ride"
    vehicle = "vehicle"
    user = "user"

class ReviewBase(BaseModel):
    type: ReviewType
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    rental_id: Optional[int] = None
    ride_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    target_user_id: Optional[int] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewOut(BaseModel):
    id: int
    type: str
    rating: int
    comment: Optional[str]
    user_id: int
    target_user_id: Optional[int]

    class Config:
        from_attributes = True
