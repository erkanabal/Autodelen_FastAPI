from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum

# ENUM for User Role
class UserRoleEnum(str, Enum):
    owner = "owner"
    renter = "renter"
    passenger = "passenger"
    admin = "admin"

# Ortak Base Model (Tarih formatlamak için)
class BaseOutModel(BaseModel):
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M")
        }

# USER SCHEMAS
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: UserRoleEnum

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserOut(UserBase, BaseOutModel):
    id: int
    role: UserRoleEnum

class Token(BaseModel):
    access_token: str
    token_type: str

# VEHICLE SCHEMAS
class VehicleBase(BaseModel):
    brand: str
    model: str
    license_plate: str
    seats: int
    luggage: Optional[int] = None

class VehicleCreate(VehicleBase):
    pass

class VehicleOut(VehicleBase, BaseOutModel):
    id: int
    owner_id: int
    available: bool

# RENTAL SCHEMAS
class RentalBase(BaseModel):
    vehicle_id: int
    start_date: datetime = Field(..., example="2025-05-20 10:00")
    end_date: datetime = Field(..., example="2025-05-22 18:30")
    total_price: Optional[int] = None  

class RentalCreate(RentalBase):
    pass

class RentalOut(RentalBase, BaseOutModel):
    id: int
    user_id: int

# RIDE SCHEMAS
class RideBase(BaseModel):
    start_date: datetime = Field(..., example="2025-06-01 09:00")
    end_date: datetime = Field(..., example="2025-06-01 11:30")
    start_location: str
    end_location: str
    available_seats: int

class RideCreate(RideBase):
    rental_id: int

class RideOut(RideBase, BaseOutModel):
    id: int
    rental_id: int
    renter_id: int

# RIDE PARTICIPANT SCHEMAS
class RideParticipantBase(BaseModel):
    ride_id: int
    passengers_count: int = Field(default=1, ge=1)

class RideParticipantCreate(RideParticipantBase):
    pass

class RideParticipantOut(RideParticipantBase, BaseOutModel):
    id: int
    user_id: int
    ride_id: int