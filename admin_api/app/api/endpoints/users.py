from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...schemas.user import User, UserWithBorrowedBooks
from ...services import user_service

router = APIRouter()

@router.get("/", response_model=List[User])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all users enrolled in the library"""
    return user_service.get_users(db=db, skip=skip, limit=limit)

@router.get("/borrowed-books/", response_model=List[UserWithBorrowedBooks])
def list_users_with_borrowed_books(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all users who have borrowed books"""
    return user_service.get_users_with_borrowed_books(db=db, skip=skip, limit=limit)

@router.get("/{user_id}/borrowed-books/", response_model=UserWithBorrowedBooks)
def get_user_borrowed_books(user_id: int, db: Session = Depends(get_db)):
    """Get details of books borrowed by a specific user"""
    user = user_service.get_user_with_borrowed_books(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
