from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas, auth, models
from app.database import get_db

router = APIRouter(prefix="/rentals", tags=["Rentals"])

@router.post("/", response_model=schemas.RentalOut, status_code=status.HTTP_201_CREATED)
def create_rental(rental: schemas.RentalCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role not in [models.UserRoleEnum.renter, models.UserRoleEnum.passenger]:
        raise HTTPException(status_code=403, detail="Only renters or passengers can rent vehicles")
    return crud.create_rental(db, rental, user_id=current_user.id)

@router.get("/", response_model=List[schemas.RentalOut])
def read_rentals(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role == models.UserRoleEnum.admin:
        return crud.get_all_rentals(db)
    elif current_user.role in [models.UserRoleEnum.renter, models.UserRoleEnum.passenger]:
        return crud.get_user_rentals(db, user_id=current_user.id)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

@router.get("/{rental_id}", response_model=schemas.RentalOut)
def read_rental(rental_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    rental = crud.get_rental(db, rental_id)
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    if current_user.role == models.UserRoleEnum.admin \
        or (current_user.role in [models.UserRoleEnum.renter, models.UserRoleEnum.passenger] and rental.renter_id == current_user.id):
        return rental
    raise HTTPException(status_code=403, detail="Not authorized")

@router.put("/{rental_id}", response_model=schemas.RentalOut)
def update_rental(rental_id: int, rental: schemas.RentalCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != models.UserRoleEnum.admin:
        raise HTTPException(status_code=403, detail="Only admin can update rentals")
    updated = crud.update_rental(db, rental_id, rental)
    if not updated:
        raise HTTPException(status_code=404, detail="Rental not found")
    return updated

@router.delete("/{rental_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rental(rental_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != models.UserRoleEnum.admin:
        raise HTTPException(status_code=403, detail="Only admin can delete rentals")
    deleted = crud.delete_rental(db, rental_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Rental not found")
    return
