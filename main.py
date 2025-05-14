from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

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

# Jinja2 templates directory
templates = Jinja2Templates(directory="app/templates")


# Route to serve the available vehicles HTML page
@app.get("/check", response_class=HTMLResponse)
def show_available_page(request: Request):
    return templates.TemplateResponse("available.html", {"request": request})

# API Routers
app.include_router(user_router.router, prefix="", tags=["Users"])
app.include_router(vehicle_router.router, prefix="", tags=["Vehicles"])
app.include_router(rental_router.router, prefix="", tags=["Rentals"])

# Root route
@app.get("/")
def read_root():
    return {"message": "API is up and running!"}
