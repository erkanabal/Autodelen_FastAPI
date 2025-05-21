from fastapi import FastAPI
from sqlalchemy.orm import Session
from app import models, crud, schemas
from app.database import engine, SessionLocal
from app.routers import user_router, vehicle_router, rental_router, ride_router, passenger_router, auth_router, review_router
import os




# Create all tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Car Rental API",
    version="1.0.0",
    description="API for managing users, vehicles, rentals, rides, and passengers."
)

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "default_admin_password")

from app import schemas

def create_admin_user():
    db = SessionLocal()
    admin_email = "admin@example.com"
    admin_user = crud.get_user_by_email(db, admin_email)
    if not admin_user:
        admin_create = schemas.UserCreate(
            username="admin",
            email=admin_email,
            password=ADMIN_PASSWORD,
            role="admin" 
        )
        admin_user = crud.create_user(db, admin_create)
        admin_user.role = "admin"
        db.commit()
        print("Admin user created")
    else:
        print("Admin user already exists")
    db.close()


@app.on_event("startup")
def on_startup():
    create_admin_user()

# Routers
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
