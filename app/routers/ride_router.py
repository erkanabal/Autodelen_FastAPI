from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import crud, schemas, models, auth
from app.database import get_db
from typing import Optional, List
from datetime import date, time
from sqlalchemy import Date, Time

router = APIRouter(prefix="/rides", tags=["Rides"])

@router.post(
    "/",
    response_model=schemas.RideOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new ride",
    description="Create a new ride entry with start/end locations, date, time, and available seats."
)
def create_ride(
    ride: schemas.RideCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Create a new ride.

    - Requires start and end locations, start date/time, and available seats.
    - Only authenticated users can create rides.
    """
    return crud.create_ride(db=db, ride=ride, user_id=current_user.id)


@router.get(
    "/",
    response_model=List[schemas.RideOut],
    status_code=status.HTTP_200_OK,
    summary="List rides",
    description="List rides based on user role: admin sees all, passenger sees available rides, renter sees own rides."
)
def read_rides(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Retrieve rides according to user role.

    - Admin: all rides
    - Passenger: available rides
    - Renter: their own rides
    """
    if current_user.role == models.UserRoleEnum.admin:
        return crud.get_all_rides(db)
    elif current_user.role in [models.UserRoleEnum.passenger, models.UserRoleEnum.admin]:
        return crud.get_available_rides(db)
    elif current_user.role == models.UserRoleEnum.renter:
        return crud.get_user_rides(db=db, user_id=current_user.id)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.get(
    "/{ride_id}",
    response_model=schemas.RideOut,
    status_code=status.HTTP_200_OK,
    summary="Get ride by ID",
    description="Get details of a ride by its ID. Access restricted based on user roles."
)
def read_ride(
    ride_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Retrieve a ride by ID.

    - Admin can view all rides.
    - Renters can view rides they own.
    - Passengers can view rides.
    """
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


@router.put(
    "/{ride_id}",
    response_model=schemas.RideOut,
    status_code=status.HTTP_200_OK,
    summary="Update a ride",
    description="Update ride details. Only renter or admin can update."
)
def update_ride(
    ride_id: int,
    updated_ride: schemas.RideCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Update a ride's details.

    - Only the renter who owns the ride or an admin can update.
    """
    if current_user.role not in [models.UserRoleEnum.renter, models.UserRoleEnum.admin]:
        raise HTTPException(status_code=403, detail="Not authorized to update ride")
    updated = crud.update_ride(db=db, ride_id=ride_id, updated_ride=updated_ride, user_id=current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Ride not found or not authorized")
    return updated


@router.delete(
    "/{ride_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a ride",
    description="Delete a ride. Only renter or admin can delete."
)
def delete_ride(
    ride_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Delete a ride by ID.

    - Only the renter who owns the ride or an admin can delete.
    """
    if current_user.role not in [models.UserRoleEnum.renter, models.UserRoleEnum.admin]:
        raise HTTPException(status_code=403, detail="Not authorized to delete ride")
    deleted = crud.delete_ride(db=db, ride_id=ride_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ride not found or not authorized")
    return {"detail": "Ride deleted successfully"}


@router.get(
    "/search",
    response_model=List[schemas.RideOut],
    status_code=status.HTTP_200_OK,
    summary="Search rides",
    description="Search rides by start/end location, date, time range, and minimum available seats."
)
def search_rides(
    start_location: Optional[str] = None,
    end_location: Optional[str] = None,
    date_filter: Optional[date] = None,
    time_min: Optional[time] = None,
    time_max: Optional[time] = None,
    min_seats: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Search rides by filters.

    - `start_location`: Filter rides starting near this location (partial match).
    - `end_location`: Filter rides ending near this location (partial match).
    - `date_filter`: Filter rides on this date.
    - `time_min` and `time_max`: Filter rides starting between these times.
    - `min_seats`: Filter rides with at least this many available seats.
    """
    query = db.query(models.Ride)

    if start_location:
        query = query.filter(models.Ride.start_location.ilike(f"%{start_location}%"))
    if end_location:
        query = query.filter(models.Ride.end_location.ilike(f"%{end_location}%"))
    if date_filter:
        query = query.filter(models.Ride.start_date.cast(Date) == date_filter)
    if time_min and time_max:
        query = query.filter(models.Ride.start_date.cast(Time).between(time_min, time_max))
    if min_seats:
        query = query.filter(models.Ride.available_seats >= min_seats)

    return query.all()
