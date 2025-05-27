from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app import schemas, crud, models, auth
from app.database import get_db
from typing import List, Optional

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("/", response_model=schemas.ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(
    review: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.create_review(db, review, current_user.id)

@router.get("/", response_model=List[schemas.ReviewOut])
def read_reviews(
    vehicle_id: Optional[int] = Query(None),
    ride_id: Optional[int] = Query(None),
    renter_id: Optional[int] = Query(None),
    review_type: Optional[schemas.ReviewType] = Query(None),
    db: Session = Depends(get_db)
):
    return crud.search_reviews(
        db,
        vehicle_id=vehicle_id,
        ride_id=ride_id,
        renter_id=renter_id,
        review_type=review_type
    )

@router.put("/{review_id}", response_model=schemas.ReviewOut)
def update_review(
    review_id: int,
    review_update: schemas.ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    updated_review = crud.update_review(db, review_id, review_update, current_user.id)
    if not updated_review:
        raise HTTPException(status_code=404, detail="Review not found or not authorized")
    return updated_review

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if not crud.delete_review(db, review_id, current_user.id):
        raise HTTPException(status_code=404, detail="Review not found or not authorized")
    return None