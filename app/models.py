from enum import Enum
from sqlalchemy import Column, Float, Integer, String, ForeignKey, Enum as SQLEnum, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class UserRoleEnum(str, Enum):
    owner = "owner"
    renter = "renter"
    passenger = "passenger"
    admin = "admin" 

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRoleEnum), nullable=False)

    vehicles = relationship("Vehicle", back_populates="owner")
    rentals = relationship("Rental", back_populates="user")
    rides_created = relationship("Ride", back_populates="renter")
    ride_participations = relationship("RideParticipant", back_populates="user")

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    license_plate = Column(String, unique=True, nullable=False)
    seats = Column(Integer, nullable=False)
    luggage = Column(Integer, nullable=True)
    available = Column(Boolean, default=True)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="vehicles")

class Rental(Base):
    __tablename__ = "rentals"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    total_price = Column(Float)

    vehicle = relationship("Vehicle")
    user = relationship("User", back_populates="rentals")
    rides = relationship("Ride", back_populates="rental")

class Ride(Base):
    __tablename__ = "rides"
    id = Column(Integer, primary_key=True, index=True)
    rental_id = Column(Integer, ForeignKey("rentals.id"))
    renter_id = Column(Integer, ForeignKey("users.id")) 
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    start_location = Column(String, nullable=False) 
    end_location = Column(String, nullable=False)
    available_seats = Column(Integer, nullable=False)

    rental = relationship("Rental", back_populates="rides")
    renter = relationship("User", back_populates="rides_created")
    participants = relationship("RideParticipant", back_populates="ride")
    

class RideParticipant(Base):
    __tablename__ = "ride_participants"
    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    passengers_count = Column(Integer, default=1)

    user = relationship("User", back_populates="ride_participations")
    ride = relationship("Ride", back_populates="participants")
