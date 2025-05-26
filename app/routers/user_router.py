from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import crud, schemas, auth, models
from app.database import get_db
from typing import List

router = APIRouter(prefix="/users", tags=["Users"])

@router.post(
    "/",
    response_model=schemas.UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Register a new user with username, email, password and role. Email must be unique."
)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    - Email must be unique.
    - Requires username, email, password, and role.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@router.get(
    "/",
    response_model=List[schemas.UserOut],
    status_code=status.HTTP_200_OK,
    summary="List all users",
    description="Retrieve a list of all registered users. Only admins are authorized."
)
def read_users(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """
    Get all users in the system.

    - Only accessible by admins.
    """
    if current_user.role != models.UserRoleEnum.admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud.get_all_users(db)


@router.get(
    "/me",
    response_model=schemas.UserOut,
    status_code=status.HTTP_200_OK,
    summary="Get current user's profile",
    description="Retrieve the profile information of the currently authenticated user."
)
def read_own_profile(current_user: models.User = Depends(auth.get_current_user)):
    """
    Get the profile data of the logged-in user.
    """
    return current_user


@router.put(
    "/me",
    response_model=schemas.UserOut,
    status_code=status.HTTP_200_OK,
    summary="Update current user's profile",
    description="Update username, email or password of the currently authenticated user."
)
def update_own_profile(updated_user: schemas.UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """
    Update the authenticated user's profile information.

    - Allows updating username, email, and password.
    """
    return crud.update_user(db, user_id=current_user.id, updated_user=updated_user)


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete current user's profile",
    description="Delete the currently authenticated user's account."
)
def delete_own_profile(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """
    Delete the authenticated user's account.

    - Permanently removes the user from the system.
    """
    crud.delete_user(db, user_id=current_user.id)
    # 204 No Content should not return body
