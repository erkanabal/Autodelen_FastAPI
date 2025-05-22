from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from app import models, schemas
from app.auth import get_password_hash
from app.models import UserRoleEnum
import datetime

# ----------------------- USER CRUD -----------------------

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=409, detail="Username already taken")

    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=UserRoleEnum(user.role.value)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, updated_user: schemas.UserUpdate):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if updated_user.username is not None:
        user.username = updated_user.username
    if updated_user.email is not None:
        user.email = updated_user.email
    if updated_user.password is not None:
        user.hashed_password = get_password_hash(updated_user.password)

    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return user

# ----------------------- VEHICLE CRUD -----------------------

def create_vehicle(db: Session, vehicle: schemas.VehicleCreate, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or user.role != UserRoleEnum.owner:
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
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle

def update_vehicle(db: Session, vehicle_id: int, updated_vehicle: schemas.VehicleUpdate, user_id: int):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if vehicle.owner_id != user_id:
        raise HTTPException(status_code=403, detail="You do not own this vehicle")

    for field, value in updated_vehicle.dict(exclude_unset=True).items():
        setattr(vehicle, field, value)

    db.commit()
    db.refresh(vehicle)
    return vehicle

def delete_vehicle(db: Session, vehicle_id: int, user_id: int):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if vehicle.owner_id != user_id:
        raise HTTPException(status_code=403, detail="You do not own this vehicle")

    db.delete(vehicle)
    db.commit()
    return vehicle

# ----------------------- RENTAL CRUD -----------------------

def create_rental(db: Session, rental: schemas.RentalCreate, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user.role != UserRoleEnum.renter:
        raise HTTPException(status_code=403, detail="Only renters can rent vehicles")

    if not is_vehicle_available(db, rental.vehicle_id, rental.start_date, rental.end_date):
        raise HTTPException(status_code=409, detail="Vehicle is not available for this period")

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

def update_rental(db: Session, rental_id: int, updated_rental: schemas.RentalUpdate, user_id: int):
    rental = db.query(models.Rental).filter(models.Rental.id == rental_id).first()
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    if rental.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    if not is_vehicle_available(
        db, rental.vehicle_id,
        updated_rental.start_date,
        updated_rental.end_date,
        exclude_rental_id=rental.id
    ):
        raise HTTPException(status_code=409, detail="Vehicle not available in new time slot")

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
        raise HTTPException(status_code=403, detail="Unauthorized")

    db.delete(rental)
    db.commit()
    return {"message": "Rental deleted successfully"}

def is_vehicle_available(db: Session, vehicle_id: int, start_date: datetime.datetime, end_date: datetime.datetime, exclude_rental_id: int = None) -> bool:
    query = db.query(models.Rental).filter(
        models.Rental.vehicle_id == vehicle_id,
        or_(
            and_(models.Rental.start_date <= start_date, models.Rental.end_date > start_date),
            and_(models.Rental.start_date < end_date, models.Rental.end_date >= end_date),
            and_(models.Rental.start_date >= start_date, models.Rental.end_date <= end_date)
        )
    )
    if exclude_rental_id:
        query = query.filter(models.Rental.id != exclude_rental_id)

    return query.first() is None

# ----------------------- RIDE CRUD -----------------------

def create_ride(db: Session, ride: schemas.RideCreate, user_id: int):
    rental = db.query(models.Rental).filter(models.Rental.id == ride.rental_id).first()
    if not rental or rental.user_id != user_id:
        raise HTTPException(status_code=403, detail="Invalid rental")

    db_ride = models.Ride(**ride.dict(), renter_id=user_id)
    db.add(db_ride)
    db.commit()
    db.refresh(db_ride)
    return db_ride

def get_all_rides(db: Session):
    return db.query(models.Ride).all()

def get_available_rides(db: Session):
    return db.query(models.Ride).filter(models.Ride.available_seats > 0).all()

# ----------------------- RIDE PARTICIPANT -----------------------

def join_ride(db: Session, ride_id: int, user_id: int, passengers_count: int = 1):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user.role != UserRoleEnum.passenger:
        raise HTTPException(status_code=403, detail="Only passengers can join rides")

    ride = db.query(models.Ride).filter(models.Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    if ride.available_seats < passengers_count:
        raise HTTPException(status_code=400, detail="Not enough available seats")

    if check_passenger_time_conflict(db, user_id, ride.start_date, ride.end_date):
        raise HTTPException(status_code=409, detail="You have a time conflict with another ride")

    db_participant = models.RideParticipant(
        ride_id=ride_id,
        user_id=user_id,
        passengers_count=passengers_count
    )
    db.add(db_participant)
    ride.available_seats -= passengers_count
    db.commit()
    return {"message": "Successfully joined the ride"}

def check_passenger_time_conflict(db: Session, user_id: int, start_date, end_date):
    return db.query(models.RideParticipant).join(models.Ride).filter(
        models.RideParticipant.user_id == user_id,
        or_(
            and_(models.Ride.start_date <= start_date, models.Ride.end_date > start_date),
            and_(models.Ride.start_date < end_date, models.Ride.end_date >= end_date),
            and_(models.Ride.start_date >= start_date, models.Ride.end_date <= end_date)
        )
    ).first() is not None

def get_user_joined_rides(db: Session, user_id: int):
    return db.query(models.RideParticipant).filter(models.RideParticipant.user_id == user_id).all()

# ----------------------- REVIEW CRUD -----------------------

def create_review(db: Session, review: schemas.ReviewCreate, user_id: int):
    db_review = models.Review(**review.dict(), user_id=user_id)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def get_reviews_by_rental(db: Session, rental_id: int):
    return db.query(models.Review).filter(models.Review.rental_id == rental_id).all()

def get_reviews_by_ride(db: Session, ride_id: int):
    return db.query(models.Review).filter(models.Review.ride_id == ride_id).all()

def get_reviews_by_type_and_target(db: Session, review_type: schemas.ReviewType, target_id: int):
    model = models.Review
    if review_type == schemas.ReviewType.rental:
        return db.query(model).filter(model.type == review_type, model.rental_id == target_id).all()
    elif review_type == schemas.ReviewType.ride:
        return db.query(model).filter(model.type == review_type, model.ride_id == target_id).all()
    elif review_type == schemas.ReviewType.vehicle:
        return db.query(model).filter(model.type == review_type, model.vehicle_id == target_id).all()
    elif review_type == schemas.ReviewType.user:
        return db.query(model).filter(model.type == review_type, model.target_user_id == target_id).all()
    else:
        raise HTTPException(status_code=400, detail="Invalid review type")
