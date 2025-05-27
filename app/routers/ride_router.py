from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app import schemas, crud, models, auth
from app.database import get_db
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/rides", tags=["Rides"])

@router.post("/", response_model=schemas.RideOut, status_code=status.HTTP_201_CREATED)
def create_ride(
    ride: schemas.RideCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role != models.UserRoleEnum.renter:
        raise HTTPException(status_code=403, detail="Only renters can create rides")
    
    try:
        return crud.create_ride(db, ride, current_user.id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[schemas.RideOut])
def read_rides(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role == models.UserRoleEnum.admin:
        return crud.get_all_rides(db)
    elif current_user.role == models.UserRoleEnum.renter:
        return [r for r in crud.get_all_rides(db) if r.renter_id == current_user.id]
    else:
        return crud.get_available_rides(db)

@router.get("/{ride_id}", response_model=schemas.RideOut)
def read_ride(
    ride_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    ride = crud.get_ride(db, ride_id=ride_id)
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    
    if (current_user.role == models.UserRoleEnum.renter and ride.renter_id != current_user.id and 
        current_user.role != models.UserRoleEnum.admin):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return ride

@router.put("/{ride_id}", response_model=schemas.RideOut)
def update_ride(
    ride_id: int,
    ride_update: schemas.RideUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role not in [models.UserRoleEnum.renter, models.UserRoleEnum.admin]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    ride = crud.update_ride(db, ride_id, ride_update)
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    return ride

@router.delete("/{ride_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ride(
    ride_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role not in [models.UserRoleEnum.renter, models.UserRoleEnum.admin]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if not crud.delete_ride(db, ride_id):
        raise HTTPException(status_code=404, detail="Ride not found")
    return None

@router.get("/search/available", response_model=List[schemas.RideOut])
def search_available_rides(
    start_location: Optional[str] = Query(None),
    end_location: Optional[str] = Query(None),
    min_seats: Optional[int] = Query(None, ge=1),
    db: Session = Depends(get_db)
):
    rides = crud.get_available_rides(db)
    
    if start_location:
        rides = [r for r in rides if start_location.lower() in r.start_location.lower()]
    if end_location:
        rides = [r for r in rides if end_location.lower() in r.end_location.lower()]
    if min_seats:
        rides = [r for r in rides if r.available_seats >= min_seats]
    
    return rides