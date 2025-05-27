from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app import crud, schemas, models, auth
from app.database import get_db
from datetime import datetime

router = APIRouter(prefix="/rentals", tags=["Rentals"])

@router.post("/", response_model=schemas.RentalOut, status_code=status.HTTP_201_CREATED)
def create_rental(
    rental: schemas.RentalCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Create a new rental.

    Only users with the 'renter' role can create rentals.
    Checks if the vehicle is available for the specified date range.
    """
    if current_user.role != models.UserRoleEnum.renter:
        raise HTTPException(status_code=403, detail="Only renters can create rentals")

    if rental.start_date >= rental.end_date:
        raise HTTPException(status_code=400, detail="start_date must be before end_date")

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


@router.get("/", response_model=list[schemas.RentalOut], status_code=status.HTTP_200_OK)
def read_rentals(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Get rentals based on user role.

    - Admin: returns all rentals.
    - Owner: returns rentals of their vehicles.
    - Renter: returns their own rentals.
    """
    if current_user.role == models.UserRoleEnum.admin:
        return crud.get_all_rentals(db)

    elif current_user.role == models.UserRoleEnum.owner:
        return crud.get_rentals_for_owner_vehicles(db, owner_id=current_user.id)

    elif current_user.role == models.UserRoleEnum.renter:
        return crud.get_all_rentals(db=db, user_id=current_user.id)

    else:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.put("/{rental_id}", response_model=schemas.RentalOut, status_code=status.HTTP_200_OK)
def update_rental(
    rental_id: int,
    updated_rental: schemas.RentalCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Update an existing rental.

    Only renters and admins are authorized to update rentals.
    """
    if current_user.role not in [models.UserRoleEnum.renter, models.UserRoleEnum.admin]:
        raise HTTPException(status_code=403, detail="Not authorized to update rental")

    return crud.update_rental(db=db, rental_id=rental_id, updated_rental=updated_rental, user_id=current_user.id)


@router.delete("/{rental_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rental(
    rental_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Delete a rental by ID.

    Only renters and admins are authorized to delete rentals.
    """
    if current_user.role not in [models.UserRoleEnum.renter, models.UserRoleEnum.admin]:
        raise HTTPException(status_code=403, detail="Not authorized to delete rental")

    deleted = crud.delete_rental(db=db, rental_id=rental_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Rental not found or not authorized")

    return {"detail": "Rental deleted successfully"}

@router.get("/available", response_model=list[schemas.VehicleOut], status_code=status.HTTP_200_OK)
def get_available_vehicles(
    start_date: str = Query(
        ...,
        example="2025-05-19 10:00",
        description="Start datetime for availability check. Format: YYYY-MM-DD HH:MM"
    ),
    end_date: str = Query(
        ...,
        example="2025-05-20 10:00",
        description="End datetime for availability check. Format: YYYY-MM-DD HH:MM"
    ),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Get all vehicles available within the specified date and time range.

    Only renters and admins can access this endpoint.
    """
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Expected: YYYY-MM-DD HH:MM")

    if start_dt >= end_dt:
        raise HTTPException(status_code=400, detail="start_date must be before end_date")

    if current_user.role not in [models.UserRoleEnum.renter, models.UserRoleEnum.admin]:
        raise HTTPException(status_code=403, detail="Not authorized")

    # ✅ This part must NOT be inside the `if` block!
    result = crud.get_available_vehicles_by_date_range(db=db, start_date=start_dt, end_date=end_dt)
    return result or []  # fallback to empty list if None is returned
