from sqlalchemy.orm import Session
from app import models, schemas
from fastapi import HTTPException, status
from app.auth import get_password_hash
from sqlalchemy import and_, or_
from app.models import UserRoleEnum
import datetime



# ----------------------- USER -----------------------

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role  # role opsiyonel, admin vs için
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, updated_user: schemas.UserUpdate):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.username = updated_user.username
        user.email = updated_user.email
        if updated_user.password:
            user.hashed_password = get_password_hash(updated_user.password)
        db.commit()
        db.refresh(user)
        return user
    return None

def delete_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return user
    return None

# ----------------------- VEHICLES (OWNER) -----------------------

def create_vehicle(db: Session, vehicle: schemas.VehicleCreate, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user.role != UserRoleEnum.owner:
        raise HTTPException(status_code=403, detail="Only owners can create vehicles")

    db_vehicle = models.Vehicle(**vehicle.dict(), owner_id=user_id)
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

def get_all_vehicles(db: Session):
    return db.query(models.Vehicle).all()

def get_all_available_vehicles(db: Session):
    return db.query(models.Vehicle).filter(models.Vehicle.available == True).all()

def get_vehicle(db: Session, vehicle_id: int):
    return db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()

def update_vehicle(db: Session, vehicle_id: int, updated_vehicle: schemas.VehicleCreate, user_id: int):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if vehicle and vehicle.owner_id == user_id:
        vehicle.brand = updated_vehicle.brand
        vehicle.model = updated_vehicle.model
        vehicle.license_plate = updated_vehicle.license_plate
        vehicle.seats = updated_vehicle.seats
        vehicle.luggage = updated_vehicle.luggage
        vehicle.available = updated_vehicle.available
        db.commit()
        db.refresh(vehicle)
        return vehicle
    return None

def delete_vehicle(db: Session, vehicle_id: int, user_id: int):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if vehicle and vehicle.owner_id == user_id:
        db.delete(vehicle)
        db.commit()
        return vehicle
    return None

# ----------------------- RENTAL (RENTER) -----------------------

def create_rental(db: Session, rental: schemas.RentalCreate, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user.role != UserRoleEnum.renter:
        raise HTTPException(status_code=403, detail="Only renters can rent vehicles")

    db_rental = models.Rental(**rental.dict(), user_id=user_id)
    db.add(db_rental)
    db.commit()
    db.refresh(db_rental)
    return db_rental

def get_all_rentals(db: Session, user_id: int | None = None):
    query = db.query(models.Rental)
    if user_id:
        query = query.filter(models.Rental.user_id == user_id)
    return query.all()


def update_rental(db: Session, rental_id: int, updated_rental: schemas.RentalCreate, user_id: int):
    rental = db.query(models.Rental).filter(models.Rental.id == rental_id).first()
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    if rental.user_id != user_id:
        raise HTTPException(status_code=403, detail="You can only update your own rentals")

    is_available = is_vehicle_available(
        db=db,
        vehicle_id=rental.vehicle_id,
        start_date=updated_rental.start_date,
        end_date=updated_rental.end_date
    )
    if not is_available:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Vehicle not available during selected period")

    rental.start_date = updated_rental.start_date
    rental.end_date = updated_rental.end_date
    db.commit()
    db.refresh(rental)
    return rental

def delete_rental(db: Session, rental_id: int, user_id: int):
    rental = db.query(models.Rental).filter(models.Rental.id == rental_id).first()
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    if rental.user_id != user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own rentals")

    db.delete(rental)
    db.commit()
    return {"message": "Rental deleted successfully"}

def is_vehicle_available(db: Session, vehicle_id: int, start_date: datetime.datetime, end_date: datetime.datetime) -> bool:
    overlapping_rentals = db.query(models.Rental).filter(
        models.Rental.vehicle_id == vehicle_id,
        or_(
            and_(models.Rental.start_date <= start_date, models.Rental.end_date > start_date),
            and_(models.Rental.start_date < end_date, models.Rental.end_date >= end_date),
            and_(models.Rental.start_date >= start_date, models.Rental.end_date <= end_date)
        )
    ).first()
    return overlapping_rentals is None

# ----------------------- RIDE (RENTER) -----------------------

def create_ride(db: Session, ride: schemas.RideCreate, user_id: int):
    db_ride = models.Ride(
        rental_id=ride.rental_id,
        start_date=ride.start_date,
        end_date=ride.end_date,
        start_location=ride.start_location,
        end_location=ride.end_location,
        available_seats=ride.available_seats,
        renter_id=user_id  
    )
    db.add(db_ride)
    db.commit()
    db.refresh(db_ride)
    return db_ride

def get_all_rides(db: Session):
    return db.query(models.Ride).all()

def get_available_rides(db: Session):
    return db.query(models.Ride).filter(models.Ride.available_seats > 0).all()

# ----------------------- RIDE PARTICIPANT (PASSENGER) -----------------------

def join_ride(db: Session, ride_id: int, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user.role != UserRoleEnum.passenger:
        raise HTTPException(status_code=403, detail="Only passengers can join rides")

    ride = db.query(models.Ride).filter(models.Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    if ride.available_seats <= 0:
        raise HTTPException(status_code=400, detail="No available seats in this ride")

    if check_passenger_time_conflict(db, user_id, ride.start_date, ride.end_date):
        raise HTTPException(status_code=409, detail="You have already joined another ride during this time")

    db_participant = models.RideParticipant(ride_id=ride_id, user_id=user_id)
    db.add(db_participant)

    ride.available_seats -= 1
    db.commit()
    return {"message": "Successfully joined the ride"}

def check_passenger_time_conflict(db: Session, user_id: int, start_date, end_date):
    conflict = db.query(models.RideParticipant).join(models.Ride).filter(
        models.RideParticipant.user_id == user_id,
        or_(
            and_(models.Ride.start_date <= start_date, models.Ride.end_date > start_date),
            and_(models.Ride.start_date < end_date, models.Ride.end_date >= end_date),
            and_(models.Ride.start_date >= start_date, models.Ride.end_date <= end_date)
        )
    ).first()
    return conflict is not None

def get_user_joined_rides(db: Session, user_id: int):
    return db.query(models.RideParticipant).filter(models.RideParticipant.user_id == user_id).all()


def create_review(db: Session, review: schemas.ReviewCreate, user_id: int):
    db_review = models.Review(**review.dict(), user_id=user_id)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def get_reviews_by_rental(db: Session, rental_id: int):
    return db.query(models.Review).filter(models.Review.rental_id == rental_id).all()

def create_review(db: Session, review: schemas.ReviewCreate, user_id: int):
    db_review = models.Review(**review.dict(), user_id=user_id)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


def get_reviews_by_type_and_target(db: Session, review_type: schemas.ReviewType, target_id: int):
    model = models.Review
    match review_type:
        case schemas.ReviewType.rental:
            return db.query(model).filter(model.type == review_type, model.rental_id == target_id).all()
        case schemas.ReviewType.ride:
            return db.query(model).filter(model.type == review_type, model.ride_id == target_id).all()
        case schemas.ReviewType.vehicle:
            return db.query(model).filter(model.type == review_type, model.vehicle_id == target_id).all()
        case schemas.ReviewType.user:
            return db.query(model).filter(model.type == review_type, model.target_user_id == target_id).all()
