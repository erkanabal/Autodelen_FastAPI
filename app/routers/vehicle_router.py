from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import crud, schemas, auth, models
from app.database import get_db
from typing import Optional, List

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])

@router.post("/", response_model=schemas.VehicleOut, status_code=status.HTTP_201_CREATED)
def create_vehicle(vehicle: schemas.VehicleCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != models.UserRoleEnum.owner:
        raise HTTPException(status_code=403, detail="Only owners can add vehicles")
    return crud.create_vehicle(db=db, vehicle=vehicle, user_id=current_user.id)

@router.get("/", response_model=list[schemas.VehicleOut], status_code=status.HTTP_200_OK)
def read_vehicles(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role == models.UserRoleEnum.admin:
        # Admin tüm araçları görür
        return crud.get_all_vehicles(db)
    elif current_user.role == models.UserRoleEnum.owner:
        # Owner sadece kendi araçlarını görür
        return crud.get_user_vehicles(db=db, user_id=current_user.id)
    elif current_user.role in [models.UserRoleEnum.renter, models.UserRoleEnum.passenger]:
        # Kiracı ve yolcu sadece uygun araçları görür
        return crud.get_all_available_vehicles(db=db)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

@router.get("/{vehicle_id}", response_model=schemas.VehicleOut, status_code=status.HTTP_200_OK)
def read_vehicle(vehicle_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    vehicle = crud.get_vehicle(db=db, vehicle_id=vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    if current_user.role == models.UserRoleEnum.admin:
        return vehicle
    if current_user.role == models.UserRoleEnum.owner and vehicle.owner_id == current_user.id:
        return vehicle
    if current_user.role in [models.UserRoleEnum.renter, models.UserRoleEnum.passenger]:
        # kiracı veya yolcu araçları görebilir
        return vehicle

    raise HTTPException(status_code=403, detail="Not authorized")

@router.put("/{vehicle_id}", response_model=schemas.VehicleOut, status_code=status.HTTP_200_OK)
def update_vehicle(vehicle_id: int, vehicle: schemas.VehicleCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role == models.UserRoleEnum.admin:
        updated = crud.update_vehicle(db=db, vehicle_id=vehicle_id, updated_vehicle=vehicle, user_id=None)
        if not updated:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        return updated

    if current_user.role == models.UserRoleEnum.owner:
        updated = crud.update_vehicle(db=db, vehicle_id=vehicle_id, updated_vehicle=vehicle, user_id=current_user.id)
        if not updated:
            raise HTTPException(status_code=403, detail="Not authorized or vehicle not found")
        return updated

    raise HTTPException(status_code=403, detail="Not authorized")

@router.delete("/{vehicle_id}, status_code=status.HTTP_204_NO_CONTENT")
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role == models.UserRoleEnum.admin:
        deleted = crud.delete_vehicle(db=db, vehicle_id=vehicle_id, user_id=None)
        if not deleted:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        return {"detail": "Vehicle deleted"}

    if current_user.role == models.UserRoleEnum.owner:
        deleted = crud.delete_vehicle(db=db, vehicle_id=vehicle_id, user_id=current_user.id)
        if not deleted:
            raise HTTPException(status_code=403, detail="Not authorized or vehicle not found")
        return {"detail": "Vehicle deleted"}

    raise HTTPException(status_code=403, detail="Not authorized")

@router.get("/search", response_model=list[schemas.VehicleOut], status_code=status.HTTP_200_OK)
def search_vehicles(
    brand: Optional[str] = None,
    model: Optional[str] = None,
    seats: Optional[int] = None,
    luggage_min: Optional[int] = None,
    available: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    query = db.query(models.Vehicle)

    if brand:
        query = query.filter(models.Vehicle.brand.ilike(f"%{brand}%"))
    if model:
        query = query.filter(models.Vehicle.model.ilike(f"%{model}%"))
    if seats:
        query = query.filter(models.Vehicle.seats >= seats)
    if luggage_min:
        query = query.filter(models.Vehicle.luggage >= luggage_min)
    if available is not None:
        query = query.filter(models.Vehicle.available == available)

    return query.all()



