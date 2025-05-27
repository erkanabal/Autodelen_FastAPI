from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app import schemas, crud, models, auth
from app.database import get_db
from typing import List
from datetime import datetime

router = APIRouter(prefix="/rentals", tags=["Rentals"])

@router.post("/", response_model=schemas.RentalOut, status_code=status.HTTP_201_CREATED)
def create_rental(
    rental: schemas.RentalCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role != models.UserRoleEnum.renter:
        raise HTTPException(status_code=403, detail="Only renters can create rentals")
    
    if rental.start_date >= rental.end_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")
    
    if not crud.is_vehicle_available(db, rental.vehicle_id, rental.start_date, rental.end_date):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vehicle not available for the selected dates"
        )
    
    return crud.create_rental(db=db, rental=rental, user_id=current_user.id)

@router.get("/", response_model=List[schemas.RentalOut])
def read_rentals(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role == models.UserRoleEnum.admin:
        return crud.get_all_rentals(db)
    elif current_user.role == models.UserRoleEnum.owner:
        return crud.get_rentals_for_owner_vehicles(db, current_user.id)
    elif current_user.role == models.UserRoleEnum.renter:
        return crud.get_all_rentals(db, current_user.id)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

@router.get("/{rental_id}", response_model=schemas.RentalOut)
def read_rental(
    rental_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    rental = crud.get_rental(db, rental_id=rental_id)
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    
    if (current_user.role == models.UserRoleEnum.renter and rental.user_id != current_user.id) or \
       (current_user.role == models.UserRoleEnum.owner and rental.vehicle.owner_id != current_user.id) or \
       (current_user.role == models.UserRoleEnum.passenger):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return rental

@router.put("/{rental_id}", response_model=schemas.RentalOut)
def update_rental(
    rental_id: int,
    rental_update: schemas.RentalCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role not in [models.UserRoleEnum.renter, models.UserRoleEnum.admin]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    rental = crud.update_rental(db, rental_id, rental_update, current_user.id)
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found or not authorized")
    return rental

@router.delete("/{rental_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rental(
    rental_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role not in [models.UserRoleEnum.renter, models.UserRoleEnum.admin]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if not crud.delete_rental(db, rental_id, current_user.id):
        raise HTTPException(status_code=404, detail="Rental not found or not authorized")
    return None

@router.get("/available/vehicles", response_model=List[schemas.VehicleOut])
def get_available_vehicles(
    start_date: str = Query(..., description="Format: YYYY-MM-DD HH:MM"),
    end_date: str = Query(..., description="Format: YYYY-MM-DD HH:MM"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    
    if start_dt >= end_dt:
        raise HTTPException(status_code=400, detail="End date must be after start date")
    
    if current_user.role not in [models.UserRoleEnum.renter, models.UserRoleEnum.admin]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return crud.get_available_vehicles_by_date_range(db, start_dt, end_dt)