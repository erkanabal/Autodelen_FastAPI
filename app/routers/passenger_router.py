from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, crud, models, auth
from app.database import get_db
from typing import List

router = APIRouter(prefix="/passengers", tags=["Passengers"])

@router.get("/rides", response_model=List[schemas.RideOut])
def read_available_rides(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role != models.UserRoleEnum.passenger:
        raise HTTPException(status_code=403, detail="Only passengers can view rides")
    return crud.get_available_rides(db)

@router.post("/rides/{ride_id}/join", status_code=status.HTTP_201_CREATED)
def join_ride(
    ride_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role != models.UserRoleEnum.passenger:
        raise HTTPException(status_code=403, detail="Only passengers can join rides")
    
    if not crud.join_ride(db, ride_id, current_user.id):
        raise HTTPException(status_code=400, detail="Unable to join ride")
    
    return {"message": "Successfully joined the ride"}