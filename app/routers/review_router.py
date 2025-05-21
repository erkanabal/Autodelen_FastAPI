from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.database import get_db
from app.auth import get_current_user

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"]
)

@router.post("/", response_model=schemas.ReviewOut)
def create_review(
    review: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.create_review(db, review, user_id=current_user.id)


@router.get("/{review_type}/{target_id}", response_model=list[schemas.ReviewOut])
def get_reviews(
    review_type: schemas.ReviewType,
    target_id: int,
    db: Session = Depends(get_db)
):
    reviews = crud.get_reviews_by_type_and_target(db, review_type, target_id)
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found.")
    return reviews

