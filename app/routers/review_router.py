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

from typing import List, Optional
from sqlalchemy import or_
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas, auth
from app.database import get_db

@router.get("/search", response_model=List[schemas.ReviewOut])
def search_reviews(
    type: Optional[str] = None,
    min_rating: Optional[int] = None,
    max_rating: Optional[int] = None,
    comment_keyword: Optional[str] = None,
    user_id: Optional[int] = None,
    target_user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    query = db.query(models.Review)

    if type:
        query = query.filter(models.Review.type == type)
    if min_rating:
        query = query.filter(models.Review.rating >= min_rating)
    if max_rating:
        query = query.filter(models.Review.rating <= max_rating)
    if comment_keyword:
        query = query.filter(models.Review.comment.ilike(f"%{comment_keyword}%"))
    if user_id:
        query = query.filter(models.Review.user_id == user_id)
    if target_user_id:
        query = query.filter(models.Review.target_user_id == target_user_id)

    return query.all()
