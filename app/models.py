from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"  # Veritabanında oluşacak tablo adı

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Araclarla iliski
    vehicles = relationship("Vehicle", back_populates="owner")

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    brand = Column(String, index=True)
    model = Column(String)
    license_plate = Column(String, unique=True)
    seats = Column(Integer)
    luggage = Column(Integer)
    available = Column(Boolean, default=True)

    # Kullanıcı ile ilişki
    owner = relationship("User", back_populates="vehicles")
    
