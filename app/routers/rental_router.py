from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import crud, schemas, models, auth
from app.database import get_db

router = APIRouter(prefix="/rental", tags=["Rental"])

@router.post("/", response_model=schemas.RentalOut)
def create_rental(
    rental: schemas.RentalCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.create_rental(db=db, rental=rental, user_id=current_user.id)

@router.get("/", response_model=list[schemas.RentalOut])
def read_user_rentals(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.get_user_rentals(db=db, user_id=current_user.id)

