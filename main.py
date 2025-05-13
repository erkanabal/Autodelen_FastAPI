from fastapi import FastAPI
from app import models
from app.database import engine
from app.routers import user_router, vehicle_router, rental_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user_router.router)
app.include_router(vehicle_router.router)
app.include_router(rental_router.router)

@app.get("/")
def read_root():
    return {"message": "API is running!"}
