from sqlalchemy.orm import Session
from app import models, schemas
from app.auth import get_password_hash

# Kullanıcıyı e-posta ile bul
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# Yeni kullanıcı oluştur
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

# Araç oluşturma fonksiyonu
def create_vehicle(db: Session, vehicle: schemas.VehicleCreate, user_id: int):
    db_vehicle = models.Vehicle(
        **vehicle.dict(),
        owner_id=user_id
    )
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle