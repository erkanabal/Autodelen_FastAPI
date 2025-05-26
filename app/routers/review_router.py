from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from app import schemas, models, crud
from app.database import get_db
from app.auth import get_current_user

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/", response_model=schemas.ReviewOut)
def create_review(
    review: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    return crud.create_review(db, review, user)


@router.get("/", response_model=List[schemas.ReviewOut])
def read_reviews(
    vehicle_id: Optional[int] = Query(default=None),
    ride_id: Optional[int] = Query(default=None),
    renter_id: Optional[int] = Query(default=None),
    review_type: Optional[schemas.ReviewType] = Query(default=None),
    db: Session = Depends(get_db)
):
    return crud.search_reviews(
        db,
        vehicle_id=vehicle_id,
        ride_id=ride_id,
        renter_id=renter_id,
        review_type=review_type,
    )
