from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app import schemas, crud, auth
from app.database import get_db
from app.auth import get_current_user
from app import models

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user)

@router.post("/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.put("/me", response_model=schemas.UserOut)
def update_user(
    updated_user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    user = crud.update_user(db=db, user_id=current_user.id, updated_user=updated_user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/me", response_model=schemas.UserOut)
def delete_user(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    user = crud.delete_user(db=db, user_id=current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user