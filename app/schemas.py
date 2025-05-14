# schemas.py
from pydantic import BaseModel
from datetime import datetime

class RentalBase(BaseModel):
    vehicle_id: int
    start_date: datetime
    end_date: datetime
    total_price: int

class RentalCreate(BaseModel):
    vehicle_id: int
    start_date: datetime
    end_date: datetime
    total_price: int


class RentalOut(RentalBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
        
        
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):

    password: str

class UserUpdate(BaseModel):
    username: str
    email: str
    password: str


class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True
        

class Token(BaseModel):
    access_token: str
    token_type: str

class VehicleBase(BaseModel):
    brand: str
    model: str
    license_plate: str
    seats: int
    luggage: int
    available: bool

class VehicleCreate(VehicleBase):
    pass

class VehicleOut(VehicleBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True
        