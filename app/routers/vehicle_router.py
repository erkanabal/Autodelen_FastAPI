from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app import crud, schemas, auth, models
from app.database import get_db
from typing import Optional, List

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])

@router.post(
    "/",
    response_model=schemas.VehicleOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new vehicle",
    description="Only users with the 'owner' role can add new vehicles. Provide brand, model, license plate, seats, and optionally luggage capacity."
)
def create_vehicle(
    vehicle: schemas.VehicleCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Create a new vehicle in the system.

    - Only users with the 'owner' role can create vehicles.
    - Requires vehicle details such as brand, model, license plate, seats, and luggage capacity.
    """
    if current_user.role != models.UserRoleEnum.owner:
        raise HTTPException(status_code=403, detail="Only owners can add vehicles")
    return crud.create_vehicle(db=db, vehicle=vehicle, user_id=current_user.id)


@router.get(
    "/",
    response_model=List[schemas.VehicleOut],
    status_code=status.HTTP_200_OK,
    summary="List vehicles",
    description="Retrieve vehicles based on user role: admin sees all, owners see their own, renters and passengers see available vehicles."
)
def read_vehicles(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Get a list of vehicles filtered by the user's role.

    - Admins see all vehicles.
    - Owners see only their own vehicles.
    - Renters and passengers see all available vehicles.
    """
    if current_user.role == models.UserRoleEnum.admin:
        return crud.get_all_vehicles(db)
    elif current_user.role == models.UserRoleEnum.owner:
        return crud.get_all_vehicles(db=db)
    elif current_user.role in [models.UserRoleEnum.renter, models.UserRoleEnum.passenger]:
        return crud.get_all_available_vehicles(db=db)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")



@router.put(
    "/{vehicle_id}",
    response_model=schemas.VehicleOut,
    status_code=status.HTTP_200_OK,
    summary="Update a vehicle",
    description="Update vehicle info. Admins can update all, owners can update their own vehicles."
)
def update_vehicle(
    vehicle_id: int, 
    vehicle: schemas.VehicleCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Update a vehicle's information.

    - Admins can update any vehicle.
    - Owners can update only their vehicles.
    """
    if current_user.role == models.UserRoleEnum.admin:
        updated = crud.update_vehicle(db=db, vehicle_id=vehicle_id, updated_vehicle=vehicle, user_id=None)
        if not updated:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        return updated

    if current_user.role == models.UserRoleEnum.owner:
        updated = crud.update_vehicle(db=db, vehicle_id=vehicle_id, updated_vehicle=vehicle, user_id=current_user.id)
        if not updated:
            raise HTTPException(status_code=403, detail="Not authorized or vehicle not found")
        return updated

    raise HTTPException(status_code=403, detail="Not authorized")


@router.delete(
    "/{vehicle_id}",
    summary="Delete a vehicle",
    description="Delete a vehicle. Admins can delete all, owners can delete their own vehicles."
)
def delete_vehicle(
    vehicle_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Delete a vehicle by ID.

    - Admins can delete any vehicle.
    - Owners can delete only their vehicles.
    """
    if current_user.role == models.UserRoleEnum.admin:
        deleted = crud.delete_vehicle(db=db, vehicle_id=vehicle_id, user_id=None)
        if not deleted:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        return {"detail": "Vehicle deleted"}

    if current_user.role == models.UserRoleEnum.owner:
        deleted = crud.delete_vehicle(db=db, vehicle_id=vehicle_id, user_id=current_user.id)
        if not deleted:
            raise HTTPException(status_code=403, detail="Not authorized or vehicle not found")
        return {"detail": "Vehicle deleted"}

    raise HTTPException(status_code=403, detail="Not authorized")


@router.get(
    "/search",
    response_model=List[schemas.VehicleOut],
    status_code=status.HTTP_200_OK,
    summary="Search vehicles",
    description="Search vehicles by brand, model, seats, luggage capacity and availability."
)
def search_vehicles(
    brand: Optional[str] = Query(None, description="Filter by brand name"),
    model: Optional[str] = Query(None, description="Filter by model name"),
    seats: Optional[int] = Query(None, description="Minimum number of seats"),
    luggage_min: Optional[int] = Query(None, description="Minimum luggage capacity"),
    available: Optional[bool] = Query(None, description="Filter by availability status"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Search vehicles by various criteria including brand, model, seats, luggage capacity, and availability.
    """
    query = db.query(models.Vehicle)

    if brand:
        query = query.filter(models.Vehicle.brand.ilike(f"%{brand}%"))
    if model:
        query = query.filter(models.Vehicle.model.ilike(f"%{model}%"))
    if seats:
        query = query.filter(models.Vehicle.seats >= seats)
    if luggage_min:
        query = query.filter(models.Vehicle.luggage >= luggage_min)
    if available is not None:
        query = query.filter(models.Vehicle.available == available)

    return query.all()

@router.get(
    "/{vehicle_id}",
    response_model=schemas.VehicleOut,
    status_code=status.HTTP_200_OK,
    summary="Get vehicle by ID",
    description="Get detailed information about a vehicle if authorized."
)
def read_vehicle(
    vehicle_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Retrieve a specific vehicle by its ID.

    - Admins can retrieve any vehicle.
    - Owners can retrieve only their vehicles.
    - Renters and passengers can retrieve vehicles.
    """
    vehicle = crud.get_vehicle(db=db, vehicle_id=vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    if current_user.role == models.UserRoleEnum.admin:
        return vehicle
    if current_user.role == models.UserRoleEnum.owner and vehicle.owner_id == current_user.id:
        return vehicle
    if current_user.role in [models.UserRoleEnum.renter, models.UserRoleEnum.passenger]:
        return vehicle

    raise HTTPException(status_code=403, detail="Not authorized")

