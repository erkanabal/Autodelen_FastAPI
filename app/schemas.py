from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime, timezone
from enum import Enum
from app import models

def ensure_aware_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def parse_and_ensure_utc(value):
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value

class PublicUserRoleEnum(str, Enum):
    owner = "owner"
    renter = "renter"
    passenger = "passenger"

class UserRoleEnum(str, Enum):
    owner = "owner"
    renter = "renter"
    passenger = "passenger"
    admin = "admin"

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: PublicUserRoleEnum

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRoleEnum

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)

class Token(BaseModel):
    access_token: str
    token_type: str

class VehicleBase(BaseModel):
    brand: str = Field(..., min_length=2, max_length=50)
    model: str = Field(..., min_length=1, max_length=50)
    license_plate: str = Field(..., min_length=4, max_length=15)
    seats: int = Field(..., gt=0)
    luggage: Optional[int] = Field(None, ge=0)

class VehicleCreate(VehicleBase):
    pass

class VehicleOut(VehicleBase):
    id: int
    owner_id: int
    available: bool

    class Config:
        from_attributes = True

class RentalBase(BaseModel):
    vehicle_id: int
    start_date: datetime
    end_date: datetime
    total_price: Optional[float] = Field(None, ge=0)

    _normalize_start_date = validator("start_date", allow_reuse=True)(parse_and_ensure_utc)
    _normalize_end_date = validator("end_date", allow_reuse=True)(parse_and_ensure_utc)

class RentalCreate(RentalBase):
    pass

class RentalOut(RentalBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class RideBase(BaseModel):
    start_date: datetime
    end_date: datetime
    start_location: str = Field(..., min_length=2, max_length=100)
    end_location: str = Field(..., min_length=2, max_length=100)
    available_seats: int = Field(..., ge=0)

    _normalize_start_date = validator("start_date", allow_reuse=True)(parse_and_ensure_utc)
    _normalize_end_date = validator("end_date", allow_reuse=True)(parse_and_ensure_utc)

class RideCreate(RideBase):
    rental_id: int

class RideOut(RideBase):
    id: int
    rental_id: int
    renter_id: int

    class Config:
        from_attributes = True

class RideUpdate(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    start_location: Optional[str] = Field(None, min_length=2, max_length=100)
    end_location: Optional[str] = Field(None, min_length=2, max_length=100)
    available_seats: Optional[int] = Field(None, ge=0)

    _normalize_start_date = validator("start_date", allow_reuse=True)(parse_and_ensure_utc)
    _normalize_end_date = validator("end_date", allow_reuse=True)(parse_and_ensure_utc)

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


class ReviewType(str, Enum):
    vehicle = "vehicle"
    ride = "ride"
    renter = "renter"
    
class ReviewBase(BaseModel):
    type: models.ReviewType
    rating: int = Field(..., ge=0, le=10)
    comment: Optional[str] = Field(None, max_length=500)
    vehicle_id: Optional[int] = None
    ride_id: Optional[int] = None
    renter_id: Optional[int] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=0, le=10)
    comment: Optional[str] = Field(None, max_length=500)


class ReviewOut(ReviewBase):
    id: int
    user_id: int
    rating_category: str  # sadece outputta tut

    class Config:
        from_attributes = True
