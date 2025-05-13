# schemas.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class VerhuurBase(BaseModel):
    vehicle_id: int
    start_date: datetime
    end_date: datetime
    total_price: int

class VerhuurCreate(VerhuurBase):
    pass

class VerhuurOut(VerhuurBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True

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
        orm_mode = True