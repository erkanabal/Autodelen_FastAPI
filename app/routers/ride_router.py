from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas, auth, models
from app.database import get_db

router = APIRouter(prefix="/rides", tags=["Rides"])

@router.post("/", response_model=schemas.RideOut, status_code=status.HTTP_201_CREATED)
def create_ride(ride: schemas.RideCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != models.UserRoleEnum.owner:
        raise HTTPException(status_code=403, detail="Only owners can add rides")
    return crud.create_ride(db, ride, user_id=current_user.id)

@router.get("/", response_model=List[schemas.RideOut])
def read_rides(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role == models.UserRoleEnum.admin:
        return crud.get_all_rides(db)
    elif current_user.role == models.UserRoleEnum.owner:
        return crud.get_user_rides(db, user_id=current_user.id)
    elif current_user.role in [models.UserRoleEnum.renter, models.UserRoleEnum.passenger]:
        return crud.get_all_available_rides(db)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

@router.get("/{ride_id}", response_model=schemas.RideOut)
def read_ride(ride_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    ride = crud.get_ride(db, ride_id)
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    if current_user.role == models.UserRoleEnum.admin \
        or (current_user.role == models.UserRoleEnum.owner and ride.owner_id == current_user.id) \
        or current_user.role in [models.UserRoleEnum.renter, models.UserRoleEnum.passenger]:
        return ride
    raise HTTPException(status_code=403, detail="Not authorized")

@router.put("/{ride_id}", response_model=schemas.RideOut)
def update_ride(ride_id: int, ride: schemas.RideCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role not in [models.UserRoleEnum.admin, models.UserRoleEnum.owner]:
        raise HTTPException(status_code=403, detail="Not authorized")
    updated = crud.update_ride(db, ride_id, ride, user_id=None if current_user.role == models.UserRoleEnum.admin else current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Ride not found or unauthorized")
    return updated

@router.delete("/{ride_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ride(ride_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role not in [models.UserRoleEnum.admin, models.UserRoleEnum.owner]:
        raise HTTPException(status_code=403, detail="Not authorized")
    deleted = crud.delete_ride(db, ride_id, user_id=None if current_user.role == models.UserRoleEnum.admin else current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ride not found or unauthorized")
    return
