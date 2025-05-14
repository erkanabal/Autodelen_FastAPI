from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas, auth, models
from app.database import get_db

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])

@router.post("/", response_model=schemas.VehicleOut)
def create_vehicle(vehicle: schemas.VehicleCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.create_vehicle(db=db, vehicle=vehicle, user_id=current_user.id)

@router.get("/", response_model=list[schemas.VehicleOut])
def read_vehicles(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.get_user_vehicles(db=db, user_id=current_user.id)

@router.get("/{vehicle_id}", response_model=schemas.VehicleOut)
def read_vehicle(vehicle_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    vehicle = crud.get_vehicle(db=db, vehicle_id=vehicle_id)
    if not vehicle or vehicle.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this vehicle")
    return vehicle

@router.put("/{vehicle_id}", response_model=schemas.VehicleOut)
def update_vehicle(vehicle_id: int, vehicle: schemas.VehicleCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    updated_vehicle = crud.update_vehicle(db=db, vehicle_id=vehicle_id, updated_vehicle=vehicle, user_id=current_user.id)
    if not updated_vehicle:
        raise HTTPException(status_code=403, detail="Not authorized to update this vehicle or vehicle not found")
    return updated_vehicle

@router.delete("/{vehicle_id}")
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    deleted = crud.delete_vehicle(db=db, vehicle_id=vehicle_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=403, detail="Not authorized to delete this vehicle or vehicle not found")
    return {"detail": "Vehicle deleted successfully"}
