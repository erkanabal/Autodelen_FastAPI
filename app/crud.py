from sqlalchemy.orm import Session
from app import models, schemas
from app.auth import get_password_hash

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

def create_verhuur(db: Session, verhuur: schemas.VerhuurCreate, user_id: int):
    db_verhuur = models.Verhuur(**verhuur.dict(), user_id=user_id)
    db.add(db_verhuur)
    db.commit()
    db.refresh(db_verhuur)
    return db_verhuur

def get_user_verhuur(db: Session, user_id: int):
    return db.query(models.Verhuur).filter(models.Verhuur.user_id == user_id).all()
