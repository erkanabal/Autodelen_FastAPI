from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"  
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    vehicles = relationship("Vehicle", back_populates="owner")
    rentals = relationship("Rental", back_populates="user")


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

    owner = relationship("User", back_populates="vehicles")
    rentals = relationship("Rental", back_populates="vehicle")

    
from sqlalchemy import CheckConstraint

class Rental(Base):
    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    total_price = Column(Integer)

    user = relationship("User", back_populates="rentals")
    vehicle = relationship("Vehicle", back_populates="rentals")


    __table_args__ = (
        CheckConstraint('end_date > start_date', name='check_rental_dates'),
    )
