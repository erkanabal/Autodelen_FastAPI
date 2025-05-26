from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from sqlalchemy.orm import Session
from app import schemas, models, crud
from app.database import get_db
from app.auth import get_current_user

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post(
    "/",
    response_model=schemas.ReviewOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new review",
    description="Authenticated users can create a review for a vehicle, ride, or renter."
)
def create_review(
    review: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    """
    Create a new review.

    - The authenticated user must provide review details.
    - Review can be associated with a vehicle, ride, or renter.
    """
    return crud.create_review(db, review, user)


@router.get(
    "/",
    response_model=List[schemas.ReviewOut],
    summary="Retrieve reviews",
    description="Get reviews filtered optionally by vehicle, ride, renter, or review type."
)
def read_reviews(
    vehicle_id: Optional[int] = Query(None, description="Filter reviews by vehicle ID"),
    ride_id: Optional[int] = Query(None, description="Filter reviews by ride ID"),
    renter_id: Optional[int] = Query(None, description="Filter reviews by renter ID"),
    review_type: Optional[schemas.ReviewType] = Query(None, description="Filter by review type"),
    db: Session = Depends(get_db)
):
    """
    Retrieve reviews with optional filters.

    - Provide any combination of filters to narrow down results.
    """
    return crud.search_reviews(
        db,
        vehicle_id=vehicle_id,
        ride_id=ride_id,
        renter_id=renter_id,
        review_type=review_type,
    )
