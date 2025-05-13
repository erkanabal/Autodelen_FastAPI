from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app import models, schemas, crud, auth
from app.database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "API is running!"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user)


@app.post("/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/vehicles", response_model=schemas.VehicleOut)
def create_vehicle(
    vehicle: schemas.VehicleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.create_vehicle(db=db, vehicle=vehicle, user_id=current_user.id)

# Get all vehicles (only current user's vehicles)
@app.get("/vehicles", response_model=list[schemas.VehicleOut])
def read_vehicles(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.get_user_vehicles(db=db, user_id=current_user.id)

# Get a single vehicle (only if owned by the current user)
@app.get("/vehicles/{vehicle_id}", response_model=schemas.VehicleOut)
def read_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    vehicle = crud.get_vehicle(db=db, vehicle_id=vehicle_id)
    if not vehicle or vehicle.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this vehicle")
    return vehicle

# Update vehicle (only the owner can update)
@app.put("/vehicles/{vehicle_id}", response_model=schemas.VehicleOut)
def update_vehicle(
    vehicle_id: int,
    vehicle: schemas.VehicleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    updated_vehicle = crud.update_vehicle(db=db, vehicle_id=vehicle_id, updated_vehicle=vehicle, user_id=current_user.id)
    if not updated_vehicle:
        raise HTTPException(status_code=403, detail="Not authorized to update this vehicle or vehicle not found")
    return updated_vehicle

# Delete vehicle (only the owner can delete)
@app.delete("/vehicles/{vehicle_id}")
def delete_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    vehicle = crud.delete_vehicle(db=db, vehicle_id=vehicle_id, user_id=current_user.id)
    if not vehicle:
        raise HTTPException(status_code=403, detail="Not authorized to delete this vehicle or vehicle not found")
    return {"detail": "Vehicle deleted successfully"}

@app.post("/verhuur", response_model=schemas.VerhuurOut)
def create_verhuur(
    verhuur: schemas.VerhuurCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.create_verhuur(db=db, verhuur=verhuur, user_id=current_user.id)

@app.get("/verhuur", response_model=list[schemas.VerhuurOut])
def read_user_verhuur(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.get_user_verhuur(db=db, user_id=current_user.id)