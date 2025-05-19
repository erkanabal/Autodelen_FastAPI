from fastapi import FastAPI
from app import models
from app.database import engine
from app.routers import user_router, vehicle_router, rental_router

# Create all tables
models.Base.metadata.create_all(bind=engine)

# FastAPI instance
app = FastAPI(
    title="Car Rental API",
    version="1.0.0",
    description="API for managing users, vehicles, and rental operations."
)
# API Routers
app.include_router(user_router.router, prefix="", tags=["Users"])
app.include_router(vehicle_router.router, prefix="", tags=["Vehicles"])
app.include_router(rental_router.router, prefix="", tags=["Rentals"])

# Root route
@app.get("/")
def read_root():
    return {"message": "API is up and running!"}
