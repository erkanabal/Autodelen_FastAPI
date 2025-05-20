from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import crud, schemas, auth, models
from app.database import get_db
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@router.get("/", response_model=list[schemas.UserOut], status_code=status.HTTP_200_OK)
def read_users(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != models.UserRoleEnum.admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud.get_all_users(db)

@router.get("/me", response_model=schemas.UserOut, status_code=status.HTTP_200_OK)
def read_own_profile(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@router.put("/me", response_model=schemas.UserOut, status_code=status.HTTP_200_OK)
def update_own_profile(updated_user: schemas.UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.update_user(db, user_id=current_user.id, updated_user=updated_user)

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_own_profile(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    crud.delete_user(db, user_id=current_user.id)
    return {"detail": "User deleted"}
