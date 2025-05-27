from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, crud, auth, models
from app.database import get_db
from typing import List

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@router.get("/", response_model=List[schemas.UserOut])
def read_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role != models.UserRoleEnum.admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud.get_all_users(db)

@router.get("/me", response_model=schemas.UserOut)
def read_own_profile(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@router.put("/me", response_model=schemas.UserOut)
def update_own_profile(
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    updated_user = crud.update_user(db, user_id=current_user.id, user_update=user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_own_profile(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if not crud.delete_user(db, user_id=current_user.id):
        raise HTTPException(status_code=404, detail="User not found")
    return None