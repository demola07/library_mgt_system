from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.user import User
from ..models.borrow import BorrowRecord
from ..schemas.book import BookBorrowed


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get all users enrolled in the library.
    
    Args:
        db: Database session injected by FastAPI dependency system
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
    
    Returns:
        List of enrolled users
    """
    return db.query(User).offset(skip).limit(limit).all()


def get_user_with_borrowed_books(db: Session, user_id: int) -> Optional[User]:
    """Get a specific user and their borrowed books.
    
    Args:
        db: Database session injected by FastAPI dependency system
        user_id: ID of the user to retrieve
    
    Returns:
        User instance with borrowed books if found, None otherwise
    """
    return db.query(User).filter(User.id == user_id).first()


def get_users_with_borrowed_books(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get all users who have borrowed books.
    
    Args:
        db: Database session injected by FastAPI dependency system
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
    
    Returns:
        List of users who have borrowed books
    """
    return (
        db.query(User)
        .join(BorrowRecord)
        .offset(skip)
        .limit(limit)
        .all()
    )
