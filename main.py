from fastapi import FastAPI
from sqlalchemy.orm import Session
from app import models, crud, schemas
from app.database import engine, SessionLocal
from app.routers import user_router, vehicle_router, rental_router, ride_router, passenger_router, auth_router, review_router
from app.auth import get_password_hash
from app.models import UserRoleEnum  # ✅ enum burada kullanılır
import os

# Veritabanı tablolarını oluştur
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Car Rental API",
    version="1.0.0",
    description="API for managing users, vehicles, rentals, rides, and passengers."
)

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "default_admin_password")

def create_admin_user():
    db = SessionLocal()
    admin_email = "admin@example.com"
    admin_user = crud.get_user_by_email(db, admin_email)
    if not admin_user:
        hashed_password = get_password_hash(ADMIN_PASSWORD)
        admin_user = models.User(
            username="admin",
            email=admin_email,
            hashed_password=hashed_password,
            role=UserRoleEnum.admin
        )
        db.add(admin_user)
        db.commit()
        print("✅ Admin user created.")
    else:
        print("ℹ️ Admin user already exists.")
    db.close()

@app.on_event("startup")
def on_startup():
    create_admin_user()

# Router'lar
app.include_router(user_router.router)
app.include_router(auth_router.router)
app.include_router(vehicle_router.router)
app.include_router(rental_router.router)
app.include_router(ride_router.router)
app.include_router(passenger_router.router)
app.include_router(review_router.router)

@app.get("/")
def read_root():
    return {"message": "API is up and running!"}