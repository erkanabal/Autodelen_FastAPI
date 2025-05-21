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

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: UserRoleEnum 

class ReviewType(str, Enum):
    rental = "rental"
    ride = "ride"
    vehicle = "vehicle"
    user = "user"

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

class UserOut(UserBase):
    id: int
    role: UserRoleEnum

    class Config:
        from_attributes = True
        

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

class VehicleOut(VehicleBase):
    id: int
    owner_id: int
    available: bool

    class Config:
        from_attributes = True
        

# RENTAL SCHEMAS
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
        

# RIDE SCHEMAS
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
        

# RIDE PARTICIPANT SCHEMAS
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
        
from pydantic import BaseModel

class ReviewBase(BaseModel):
    rating: int
    comment: str | None = None

class ReviewCreate(ReviewBase):
    rental_id: int

class ReviewOut(ReviewBase):
    id: int
    user_id: int
    rental_id: int

    class Config:
        orm_mode = True

class ReviewBase(BaseModel):
    type: ReviewType
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = None

    rental_id: int | None = None
    ride_id: int | None = None
    vehicle_id: int | None = None
    target_user_id: int | None = None

class ReviewCreate(ReviewBase):
    pass

class ReviewOut(ReviewBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
