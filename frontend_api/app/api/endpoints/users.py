from fastapi import APIRouter, Depends, HTTPException, Path, Body
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...schemas.user import User, UserCreate
from ...services import user_service

router = APIRouter()

@router.post("/",
    response_model=User,
    summary="Create a new user"
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """Create a new user account with unique email."""
    db_user = user_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    return user_service.create_user(db=db, user=user)

@router.get("/me/{user_id}",
    response_model=User,
    summary="Get user information"
)
def read_user(
    user_id: int = Path(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific user."""
    db_user = user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return db_user
