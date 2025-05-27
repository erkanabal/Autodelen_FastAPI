from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app import schemas, crud, models, auth
from app.database import get_db
from typing import List, Optional

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])

@router.post("/", response_model=schemas.VehicleOut, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    vehicle: schemas.VehicleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role != models.UserRoleEnum.owner:
        raise HTTPException(status_code=403, detail="Only owners can create vehicles")
    return crud.create_vehicle(db=db, vehicle=vehicle, owner_id=current_user.id)

@router.get("/", response_model=List[schemas.VehicleOut])
def read_vehicles(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role == models.UserRoleEnum.admin:
        return crud.get_all_vehicles(db)
    elif current_user.role == models.UserRoleEnum.owner:
        return [v for v in crud.get_all_vehicles(db) if v.owner_id == current_user.id]
    else:
        return crud.get_all_available_vehicles(db)

@router.get("/{vehicle_id}", response_model=schemas.VehicleOut)
def read_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    vehicle = crud.get_vehicle(db, vehicle_id=vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    if (current_user.role == models.UserRoleEnum.owner and vehicle.owner_id != current_user.id and 
        current_user.role != models.UserRoleEnum.admin):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return vehicle

@router.put("/{vehicle_id}", response_model=schemas.VehicleOut)
def update_vehicle(
    vehicle_id: int,
    vehicle: schemas.VehicleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role == models.UserRoleEnum.admin:
        updated_vehicle = crud.update_vehicle(db, vehicle_id, vehicle, None)
    else:
        updated_vehicle = crud.update_vehicle(db, vehicle_id, vehicle, current_user.id)
    
    if not updated_vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found or not authorized")
    return updated_vehicle

@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role == models.UserRoleEnum.admin:
        success = crud.delete_vehicle(db, vehicle_id, None)
    else:
        success = crud.delete_vehicle(db, vehicle_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Vehicle not found or not authorized")
    return None

@router.get("/search/available", response_model=List[schemas.VehicleOut])
def search_available_vehicles(
    brand: Optional[str] = Query(None),
    model: Optional[str] = Query(None),
    min_seats: Optional[int] = Query(None, ge=1),
    min_luggage: Optional[int] = Query(None, ge=0),
    db: Session = Depends(get_db)
):
    vehicles = crud.get_all_available_vehicles(db)
    
    if brand:
        vehicles = [v for v in vehicles if brand.lower() in v.brand.lower()]
    if model:
        vehicles = [v for v in vehicles if model.lower() in v.model.lower()]
    if min_seats:
        vehicles = [v for v in vehicles if v.seats >= min_seats]
    if min_luggage:
        vehicles = [v for v in vehicles if v.luggage and v.luggage >= min_luggage]
    
    return vehicles