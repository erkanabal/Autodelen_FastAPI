from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import crud, schemas, models, auth
from app.database import get_db

router = APIRouter(prefix="/passengers", tags=["Passengers"])

@router.get("/rides", response_model=list[schemas.RideOut], status_code=status.HTTP_200_OK)
def read_available_rides(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user) 
):
    if current_user.role != models.UserRoleEnum.passenger:
        raise HTTPException(status_code=403, detail="Only passengers can view rides")
    
    return crud.get_available_rides(db=db)

@router.post("/rides/{ride_id}/join", status_code=status.HTTP_200_OK)
def join_ride(
    ride_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user) 
):
    if current_user.role != models.UserRoleEnum.passenger:
        raise HTTPException(status_code=403, detail="Only passengers can join rides")

   
    result = crud.join_ride(db=db, ride_id=ride_id, user_id=current_user.id)

    return {"detail": result["message"]}
