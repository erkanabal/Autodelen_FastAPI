from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app import crud, schemas, models, auth
from app.database import get_db
from app.utils.datetime_utils import parse_datetime_param  # DateTime parsing utility

router = APIRouter(prefix="/rentals", tags=["Rentals"])

@router.post("/", response_model=schemas.RentalOut)
def create_rental(
    rental: schemas.RentalCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Check if the vehicle is available
    is_available = crud.is_vehicle_available(
        db=db,
        vehicle_id=rental.vehicle_id,
        start_date=rental.start_date,
        end_date=rental.end_date
    )

    if not is_available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The vehicle is already rented in the selected date range."
        )

    return crud.create_rental(db=db, rental=rental, user_id=current_user.id)


@router.get("/", response_model=list[schemas.RentalOut])
def read_user_rentals(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.get_user_rentals(db=db, user_id=current_user.id)

@router.put("/{rental_id}", response_model=schemas.RentalOut)
def update_rental_endpoint(
    rental_id: int,
    updated_rental: schemas.RentalCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Kiralama güncelleme fonksiyonu
    return crud.update_rental(db=db, rental_id=rental_id, updated_rental=updated_rental, user_id=current_user.id)


@router.delete("/{rental_id}")
def delete_rental_endpoint(
    rental_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Kiralama silme fonksiyonu
    return crud.delete_rental(db=db, rental_id=rental_id, user_id=current_user.id)


@router.get("/available", response_model=list[schemas.VehicleOut])
def get_available_vehicles(
    start_date: str = Query(...),
    end_date: str = Query(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Parse the start_date and end_date with the utility function
    start_dt = parse_datetime_param(start_date)
    end_dt = parse_datetime_param(end_date)

    return crud.get_available_vehicles(db=db, start_date=start_dt, end_date=end_dt)

