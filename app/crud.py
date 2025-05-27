from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from datetime import datetime
from typing import List, Optional
from app import models, schemas
from app.auth import get_password_hash
from app.schemas import UserRoleEnum

# User CRUD operations
def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
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

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None
    
    if user_update.username:
        db_user.username = user_update.username
    if user_update.email:
        db_user.email = user_update.email
    if user_update.password:
        db_user.hashed_password = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True

def get_all_users(db: Session) -> List[models.User]:
    return db.query(models.User).all()

# Vehicle CRUD operations
def create_vehicle(db: Session, vehicle: schemas.VehicleCreate, owner_id: int) -> models.Vehicle:
    db_vehicle = models.Vehicle(**vehicle.dict(), owner_id=owner_id)
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

def get_vehicle(db: Session, vehicle_id: int) -> Optional[models.Vehicle]:
    return db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()

def get_all_vehicles(db: Session) -> List[models.Vehicle]:
    return db.query(models.Vehicle).all()

def get_all_available_vehicles(db: Session) -> List[models.Vehicle]:
    return db.query(models.Vehicle).filter(models.Vehicle.available == True).all()

def update_vehicle(
    db: Session, 
    vehicle_id: int, 
    vehicle_update: schemas.VehicleCreate, 
    owner_id: int
) -> Optional[models.Vehicle]:
    db_vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if not db_vehicle or db_vehicle.owner_id != owner_id:
        return None
    
    for key, value in vehicle_update.dict().items():
        setattr(db_vehicle, key, value)
    
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

def delete_vehicle(db: Session, vehicle_id: int, owner_id: int) -> bool:
    db_vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if not db_vehicle or db_vehicle.owner_id != owner_id:
        return False
    
    db.delete(db_vehicle)
    db.commit()
    return True

# Rental CRUD operations
def create_rental(db: Session, rental: schemas.RentalCreate, user_id: int) -> models.Rental:
    db_rental = models.Rental(**rental.dict(), user_id=user_id)
    db.add(db_rental)
    db.commit()
    db.refresh(db_rental)
    return db_rental

def get_rental(db: Session, rental_id: int) -> Optional[models.Rental]:
    return db.query(models.Rental).filter(models.Rental.id == rental_id).first()

def get_all_rentals(db: Session, user_id: Optional[int] = None) -> List[models.Rental]:
    query = db.query(models.Rental)
    if user_id:
        query = query.filter(models.Rental.user_id == user_id)
    return query.all()

def get_rentals_for_owner_vehicles(db: Session, owner_id: int) -> List[models.Rental]:
    return db.query(models.Rental).join(models.Vehicle).filter(models.Vehicle.owner_id == owner_id).all()

def update_rental(
    db: Session, 
    rental_id: int, 
    rental_update: schemas.RentalCreate, 
    user_id: int
) -> Optional[models.Rental]:
    db_rental = db.query(models.Rental).filter(models.Rental.id == rental_id).first()
    if not db_rental or db_rental.user_id != user_id:
        return None
    
    for key, value in rental_update.dict().items():
        setattr(db_rental, key, value)
    
    db.commit()
    db.refresh(db_rental)
    return db_rental

def delete_rental(db: Session, rental_id: int, user_id: int) -> bool:
    db_rental = db.query(models.Rental).filter(models.Rental.id == rental_id).first()
    if not db_rental or db_rental.user_id != user_id:
        return False
    
    db.delete(db_rental)
    db.commit()
    return True

def is_vehicle_available(
    db: Session, 
    vehicle_id: int, 
    start_date: datetime, 
    end_date: datetime
) -> bool:
    overlapping_rentals = db.query(models.Rental).filter(
        models.Rental.vehicle_id == vehicle_id,
        or_(
            and_(models.Rental.start_date <= start_date, models.Rental.end_date > start_date),
            and_(models.Rental.start_date < end_date, models.Rental.end_date >= end_date),
            and_(models.Rental.start_date >= start_date, models.Rental.end_date <= end_date)
        )
    ).first()
    return overlapping_rentals is None

def get_available_vehicles_by_date_range(
    db: Session, 
    start_date: datetime, 
    end_date: datetime
) -> List[models.Vehicle]:
    vehicles = db.query(models.Vehicle).filter(models.Vehicle.available == True).all()
    available_vehicles = []
    
    for vehicle in vehicles:
        if is_vehicle_available(db, vehicle.id, start_date, end_date):
            available_vehicles.append(vehicle)
    
    return available_vehicles

# Ride CRUD operations
def create_ride(db: Session, ride: schemas.RideCreate, user_id: int) -> models.Ride:

    rental = db.query(models.Rental).filter(models.Rental.id == ride.rental_id).first()

    if not rental:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rental not found"
        )


    # Normalize datetimes by removing timezone info to avoid TZ issues
    ride_start = ride.start_date.replace(tzinfo=None)
    ride_end = ride.end_date.replace(tzinfo=None)
    rental_start = rental.start_date.replace(tzinfo=None)
    rental_end = rental.end_date.replace(tzinfo=None)


    # Check if the ride dates are within the rental dates
    if not (rental_start <= ride_start and rental_end >= ride_end):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid rental found for the specified dates"
        )

    if rental.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not own this rental"
        )

    db_ride = models.Ride(
        **ride.dict(),
        renter_id=user_id
    )
    db.add(db_ride)
    db.commit()
    db.refresh(db_ride)

    return db_ride



def get_ride(db: Session, ride_id: int) -> Optional[models.Ride]:
    return db.query(models.Ride).filter(models.Ride.id == ride_id).first()

def get_all_rides(db: Session) -> List[models.Ride]:
    return db.query(models.Ride).all()

def get_available_rides(db: Session) -> List[models.Ride]:
    return db.query(models.Ride).filter(models.Ride.available_seats > 0).all()

def update_ride(
    db: Session, 
    ride_id: int, 
    ride_update: schemas.RideUpdate
) -> Optional[models.Ride]:
    db_ride = db.query(models.Ride).filter(models.Ride.id == ride_id).first()
    if not db_ride:
        return None
    
    for key, value in ride_update.dict(exclude_unset=True).items():
        setattr(db_ride, key, value)
    
    db.commit()
    db.refresh(db_ride)
    return db_ride

def delete_ride(db: Session, ride_id: int) -> bool:
    db_ride = db.query(models.Ride).filter(models.Ride.id == ride_id).first()
    if not db_ride:
        return False
    
    db.delete(db_ride)
    db.commit()
    return True

# Ride Participant CRUD operations
def join_ride(db: Session, ride_id: int, user_id: int) -> bool:
    ride = db.query(models.Ride).filter(models.Ride.id == ride_id).first()
    if not ride or ride.available_seats <= 0:
        return False
    
    if check_passenger_time_conflict(db, user_id, ride.start_date, ride.end_date):
        return False
    
    participant = models.RideParticipant(
        ride_id=ride_id,
        user_id=user_id
    )
    db.add(participant)
    ride.available_seats -= 1
    db.commit()
    return True

def check_passenger_time_conflict(
    db: Session, 
    user_id: int, 
    start_date: datetime, 
    end_date: datetime
) -> bool:
    conflict = db.query(models.RideParticipant).join(models.Ride).filter(
        models.RideParticipant.user_id == user_id,
        or_(
            and_(models.Ride.start_date <= start_date, models.Ride.end_date > start_date),
            and_(models.Ride.start_date < end_date, models.Ride.end_date >= end_date),
            and_(models.Ride.start_date >= start_date, models.Ride.end_date <= end_date)
        )
    ).first()
    return conflict is not None

def get_user_joined_rides(db: Session, user_id: int) -> List[models.RideParticipant]:
    return db.query(models.RideParticipant).filter(models.RideParticipant.user_id == user_id).all()

# Review CRUD operations
def create_review(db: Session, review: schemas.ReviewCreate, user_id: int) -> models.Review:
    review_data = review.dict(exclude={"rating_category"})  # rating_category inputta yok ama ek güvenlik
    db_review = models.Review(
        **review_data,
        user_id=user_id,
        rating_category=categorize_rating(review.rating)
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def get_review(db: Session, review_id: int) -> Optional[models.Review]:
    return db.query(models.Review).filter(models.Review.id == review_id).first()

def search_reviews(
    db: Session,
    vehicle_id: Optional[int] = None,
    ride_id: Optional[int] = None,
    renter_id: Optional[int] = None,
    review_type: Optional[models.ReviewType] = None
) -> List[models.Review]:
    query = db.query(models.Review)
    
    if vehicle_id:
        query = query.filter(models.Review.vehicle_id == vehicle_id)
    if ride_id:
        query = query.filter(models.Review.ride_id == ride_id)
    if renter_id:
        query = query.filter(models.Review.renter_id == renter_id)
    if review_type:
        query = query.filter(models.Review.type == review_type)
    
    return query.all()

def update_review(
    db: Session, 
    review_id: int, 
    review_update: schemas.ReviewUpdate, 
    user_id: int
) -> Optional[models.Review]:
    db_review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not db_review or db_review.user_id != user_id:
        return None
    
    update_data = review_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_review, key, value)
    
    if 'rating' in update_data:
        db_review.rating_category = categorize_rating(update_data['rating'])
    
    db.commit()
    db.refresh(db_review)
    return db_review

def delete_review(db: Session, review_id: int, user_id: int) -> bool:
    db_review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not db_review or db_review.user_id != user_id:
        return False
    
    db.delete(db_review)
    db.commit()
    return True

def categorize_rating(rating: int) -> str:
    if rating >= 9:
        return "Excellent"
    elif rating >= 7:
        return "Very Good"
    elif rating >= 5:
        return "Good"
    elif rating >= 3:
        return "Fair"
    else:
        return "Poor"
