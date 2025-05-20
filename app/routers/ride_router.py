from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import crud, schemas, models, auth
from app.database import get_db

router = APIRouter(prefix="/rides", tags=["Rides"])

@router.post("/", response_model=schemas.RideOut, status_code=status.HTTP_201_CREATED)
def create_ride(
    ride: schemas.RideCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.create_ride(db=db, ride=ride, user_id=current_user.id)

@router.get("/", response_model=list[schemas.RideOut], status_code=status.HTTP_200_OK)
def read_rides(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role == models.UserRoleEnum.admin:
        return crud.get_all_rides(db)
    elif current_user.role in [models.UserRoleEnum.passenger, models.UserRoleEnum.admin]:
        return crud.get_available_rides(db)
    elif current_user.role == models.UserRoleEnum.renter:
        return crud.get_user_rides(db=db, user_id=current_user.id)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

@router.get("/{ride_id}", response_model=schemas.RideOut, status_code=status.HTTP_200_OK)
def read_ride(ride_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    ride = crud.get_ride(db=db, ride_id=ride_id)
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    if current_user.role == models.UserRoleEnum.admin:
        return ride
    if current_user.role == models.UserRoleEnum.renter and ride.renter_id == current_user.id:
        return ride
    if current_user.role == models.UserRoleEnum.passenger:
        return ride

    raise HTTPException(status_code=403, detail="Not authorized")

@router.put("/{ride_id}", response_model=schemas.RideOut, status_code=status.HTTP_200_OK)
def update_ride(ride_id: int, updated_ride: schemas.RideCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != models.UserRoleEnum.renter and current_user.role != models.UserRoleEnum.admin:
        raise HTTPException(status_code=403, detail="Not authorized to update ride")
    updated = crud.update_ride(db=db, ride_id=ride_id, updated_ride=updated_ride, user_id=current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Ride not found or not authorized")
    return updated

@router.delete("/{ride_id}, status_code=status.HTTP_204_NO_CONTENT")
def delete_ride(ride_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != models.UserRoleEnum.renter and current_user.role != models.UserRoleEnum.admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete ride")
    deleted = crud.delete_ride(db=db, ride_id=ride_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ride not found or not authorized")
    return {"detail": "Ride deleted successfully"}
