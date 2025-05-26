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
    username: str = Field(..., description="Username of the user")
    email: EmailStr = Field(..., description="Email address of the user")
    password: str = Field(..., description="Password of the user")
    role: PublicUserRoleEnum = Field(..., description="Role of the user (owner, renter, passenger)")

    class Config:
        use_enum_values = False
        title = "UserCreate"
        description = "Fields required to create a new user"

class UserOut(BaseModel):
    id: int = Field(..., description="ID of the user")
    username: str = Field(..., description="Username of the user")
    email: EmailStr = Field(..., description="Email address of the user")
    role: UserRoleEnum = Field(..., description="Role of the user (owner, renter, passenger, admin)")

    class Config:
        from_attributes = True
        title = "UserOut"
        description = "User information"

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, description="Username to update")
    email: Optional[EmailStr] = Field(None, description="Email address to update")
    password: Optional[str] = Field(None, description="Password to update")

    class Config:
        title = "UserUpdate"
        description = "Optional fields to update user information"

# ====================
# TOKEN SCHEMAS
# ====================

class Token(BaseModel):
    access_token: str = Field(..., description="Access token string")
    token_type: str = Field(..., description="Type of the token (e.g., Bearer)")

    class Config:
        title = "Token"
        description = "JWT token details"

# ====================
# VEHICLE SCHEMAS
# ====================

class VehicleBase(BaseModel):
    brand: str = Field(..., description="Brand of the vehicle")
    model: str = Field(..., description="Model of the vehicle")
    license_plate: str = Field(..., description="License plate number")
    seats: int = Field(..., description="Number of seats")
    luggage: Optional[int] = Field(None, description="Luggage capacity (optional)")

    class Config:
        title = "VehicleBase"
        description = "Basic vehicle information"

class VehicleCreate(VehicleBase):
    class Config:
        title = "VehicleCreate"
        description = "Fields required to create a new vehicle"

class VehicleOut(VehicleBase):
    id: int = Field(..., description="Vehicle ID")
    owner_id: int = Field(..., description="ID of the vehicle owner")
    available: bool = Field(..., description="Availability status of the vehicle")

    class Config:
        from_attributes = True
        title = "VehicleOut"
        description = "Detailed vehicle information"

# ====================
# RENTAL SCHEMAS
# ====================

class RentalBase(BaseModel):
    vehicle_id: int = Field(..., description="ID of the rented vehicle")
    start_date: datetime = Field(..., description="Rental start date and time")
    end_date: datetime = Field(..., description="Rental end date and time")
    total_price: Optional[float] = Field(None, description="Total price of the rental")

    class Config:
        title = "RentalBase"
        description = "Basic rental information"

class RentalCreate(RentalBase):
    class Config:
        title = "RentalCreate"
        description = "Fields required to create a new rental"

class RentalOut(RentalBase):
    id: int = Field(..., description="Rental ID")
    user_id: int = Field(..., description="ID of the user who made the rental")

    class Config:
        from_attributes = True
        title = "RentalOut"
        description = "Detailed rental information"

# ====================
# RIDE SCHEMAS
# ====================

class RideBase(BaseModel):
    start_date: datetime = Field(..., description="Ride start date and time")
    end_date: datetime = Field(..., description="Ride end date and time")
    start_location: str = Field(..., description="Starting location of the ride")
    end_location: str = Field(..., description="Ending location of the ride")
    available_seats: int = Field(..., description="Number of available seats")

    class Config:
        title = "RideBase"
        description = "Basic ride information"

class RideCreate(RideBase):
    rental_id: int = Field(..., description="Associated rental ID")

    class Config:
        title = "RideCreate"
        description = "Fields required to create a new ride"

class RideOut(RideBase):
    id: int = Field(..., description="Ride ID")
    rental_id: int = Field(..., description="Associated rental ID")
    renter_id: int = Field(..., description="ID of the renter")

    class Config:
        from_attributes = True
        title = "RideOut"
        description = "Detailed ride information"

# ====================
# RIDE PARTICIPANT SCHEMAS
# ====================

class RideParticipantBase(BaseModel):
    ride_id: int = Field(..., description="ID of the ride")
    passengers_count: int = Field(default=1, ge=1, description="Number of passengers (minimum 1)")

    class Config:
        title = "RideParticipantBase"
        description = "Basic ride participant information"

class RideParticipantCreate(RideParticipantBase):
    class Config:
        title = "RideParticipantCreate"
        description = "Fields required to add a ride participant"

class RideParticipantOut(RideParticipantBase):
    id: int = Field(..., description="Participant ID")
    user_id: int = Field(..., description="User ID of the participant")

    class Config:
        from_attributes = True
        title = "RideParticipantOut"
        description = "Detailed ride participant information"

# ====================
# REVIEW SCHEMAS
# ====================

class ReviewType(str, Enum):
    vehicle = "vehicle"
    ride = "ride"
    renter = "renter"

class ReviewBase(BaseModel):
    type: ReviewType = Field(..., description="Type of the review (vehicle, ride, renter)")
    rating: int = Field(..., ge=0, le=10, description="Rating score (0-10)")
    rating_category: str = Field(..., description="Category of the rating")
    comment: Optional[str] = Field(None, description="Optional comment")
    vehicle_id: Optional[int] = Field(None, description="Reviewed vehicle ID (if any)")
    ride_id: Optional[int] = Field(None, description="Reviewed ride ID (if any)")
    renter_id: Optional[int] = Field(None, description="Reviewed renter ID (if any)")

    class Config:
        title = "ReviewBase"
        description = "Basic review information"

class ReviewCreate(ReviewBase):
    class Config:
        title = "ReviewCreate"
        description = "Fields required to create a new review"

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=0, le=10, description="Updated rating score (0-10)")
    comment: Optional[str] = Field(None, description="Updated comment")

    class Config:
        title = "ReviewUpdate"
        description = "Fields to update a review"

class ReviewOut(ReviewBase):
    id: int = Field(..., description="Review ID")
    user_id: int = Field(..., description="ID of the user who created the review")

    class Config:
        from_attributes = True
        title = "ReviewOut"
        description = "Detailed review information"
