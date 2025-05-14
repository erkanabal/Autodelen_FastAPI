from sqlalchemy.orm import Session
from app import models, schemas
from fastapi import HTTPException, status
from app.auth import get_password_hash
from sqlalchemy import and_, or_
import datetime

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

# Create a new vehicle and associate it with the logged-in user
def create_vehicle(db: Session, vehicle: schemas.VehicleCreate, user_id: int):
    db_vehicle = models.Vehicle(**vehicle.dict(), owner_id=user_id)
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

# Get all vehicles for the current user
def get_user_vehicles(db: Session, user_id: int):
    return db.query(models.Vehicle).filter(models.Vehicle.owner_id == user_id).all()

# Get a single vehicle by ID
def get_vehicle(db: Session, vehicle_id: int):
    return db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()

# Update vehicle by ID (only if the current user owns the vehicle)
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

# Delete a vehicle by ID (only if the current user owns the vehicle)
def delete_vehicle(db: Session, vehicle_id: int, user_id: int):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if vehicle and vehicle.owner_id == user_id:
        db.delete(vehicle)
        db.commit()
        return vehicle
    return None

def create_rental(db: Session, rental: schemas.RentalCreate, user_id: int):
    db_rental = models.Rental(**rental.dict(), user_id=user_id)
    db.add(db_rental)
    db.commit()
    db.refresh(db_rental)
    return db_rental

def get_user_rentals(db: Session, user_id: int):
    return db.query(models.Rental).filter(models.Rental.user_id == user_id).all()

def is_vehicle_available(db: Session, vehicle_id: int, start_date: datetime, end_date: datetime) -> bool:
    overlapping_rentals = db.query(models.Rental).filter(
        models.Rental.vehicle_id == vehicle_id,
        or_(
            and_(models.Rental.start_date <= start_date, models.Rental.end_date > start_date),
            and_(models.Rental.start_date < end_date, models.Rental.end_date >= end_date),
            and_(models.Rental.start_date >= start_date, models.Rental.end_date <= end_date)
        )
    ).first()
    return overlapping_rentals is None

def get_available_vehicles(db: Session, start_date: datetime, end_date: datetime):
    conflicting_vehicle_ids = db.query(models.Rental.vehicle_id).filter(
        or_(
            and_(models.Rental.start_date <= start_date, models.Rental.end_date > start_date),
            and_(models.Rental.start_date < end_date, models.Rental.end_date >= end_date),
            and_(models.Rental.start_date >= start_date, models.Rental.end_date <= end_date)
        )
    ).all()

    print("Conflicting vehicle IDs (vehicles with rentals during the requested period):")
    for vehicle_id in conflicting_vehicle_ids:
        print(vehicle_id)

    available_vehicles = db.query(models.Vehicle).filter(
        models.Vehicle.id.notin_([vehicle_id[0] for vehicle_id in conflicting_vehicle_ids])
    ).all()

    print(f"Available vehicles count: {len(available_vehicles)}")
    return available_vehicles

def update_rental(db: Session, rental_id: int, updated_rental: schemas.RentalCreate, user_id: int):
    rental = db.query(models.Rental).filter(models.Rental.id == rental_id).first()
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    
    # Kiralama kullanıcının kendi kaydı mı?
    if rental.user_id != user_id:
        raise HTTPException(status_code=403, detail="You can only update your own rentals")
    
    # Kiralama tarihlerini kontrol et (Başka bir kiralama ile çakışmasın)
    is_available = is_vehicle_available(
        db=db,
        vehicle_id=rental.vehicle_id,
        start_date=updated_rental.start_date,
        end_date=updated_rental.end_date
    )
    
    if not is_available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The vehicle is already rented during the selected period."
        )
    
    # Kiralama bilgilerini güncelle
    rental.start_date = updated_rental.start_date
    rental.end_date = updated_rental.end_date
    db.commit()
    db.refresh(rental)
    
    return rental

def delete_rental(db: Session, rental_id: int, user_id: int):
    rental = db.query(models.Rental).filter(models.Rental.id == rental_id).first()
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    
    # Kiralama kullanıcının kendi kaydı mı?
    if rental.user_id != user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own rentals")
    
    db.delete(rental)
    db.commit()
    
    return {"message": "Rental deleted successfully"}

# Kullanıcı güncelle
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

# Kullanıcı sil
def delete_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return user
    return None


