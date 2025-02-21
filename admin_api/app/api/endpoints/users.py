from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...schemas.user import UserResponse, UserWithBorrowedBooksResponse
from ...services.user_service import user_service
from shared.pagination import PaginatedResponse

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[UserResponse])
async def list_users(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """List all users enrolled in the library with pagination
    
    Args:
        page: Page number (1-based)
        limit: Maximum number of items per page
        db: Database session
    """
    return await user_service.get_users(db, page=page, limit=limit)

@router.get("/borrowed-books", response_model=PaginatedResponse[UserWithBorrowedBooksResponse])
async def list_users_with_borrowed_books(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """List all users who have borrowed books with pagination
    
    Args:
        page: Page number (1-based)
        limit: Maximum number of items per page
        db: Database session
    """
    return await user_service.get_users_with_borrowed_books(db, page=page, limit=limit)


