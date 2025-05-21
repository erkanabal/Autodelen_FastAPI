from enum import Enum
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum as SQLEnum, DateTime, Text
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

    # 🔧 Yapan kullanıcı
    reviews = relationship("Review", back_populates="user", foreign_keys="Review.user_id")

    # 🔧 Bu kullanıcıya yapılan yorumlar (örneğin user-to-user)
    received_reviews = relationship("Review", back_populates="target_user", foreign_keys="Review.target_user_id")



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

    reviews = relationship("Review", back_populates="rental")


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

class ReviewType(str, Enum):
    rental = "rental"
    ride = "ride"
    vehicle = "vehicle"
    user = "user"

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(SQLEnum(ReviewType), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    rental_id = Column(Integer, ForeignKey("rentals.id"), nullable=True)
    ride_id = Column(Integer, ForeignKey("rides.id"), nullable=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    user = relationship("User", foreign_keys=[user_id])
    rental = relationship("Rental")
    ride = relationship("Ride")
    vehicle = relationship("Vehicle")
    target_user = relationship("User", foreign_keys=[target_user_id])
