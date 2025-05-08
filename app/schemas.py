from pydantic import BaseModel, EmailStr
from typing import Optional

# Kullanıcıdan kayıt olurken istenecek alanlar
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# Kullanıcıya geri dönecek alanlar (şifre yok!)
class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True
        

# Giriş yapan kullanıcıya dönecek JWT token bilgisi
class Token(BaseModel):
    access_token: str
    token_type: str

# Araç oluşturma
class VehicleCreate(BaseModel):
    brand: str
    model: str
    license_plate: str
    seats: int
    luggage: int
    available: Optional[bool] = True

# Araç yanıt
class VehicleOut(VehicleCreate):
    id: int
    owner_id: int

    class Config:
        from_attributes = True