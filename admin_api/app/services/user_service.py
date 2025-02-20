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
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )
    
    if user:
        # Get all active borrow records for this user with book data
        borrow_records = (
            db.query(BorrowRecord)
            .filter(BorrowRecord.user_id == user_id)
            .join(BorrowRecord.book)
            .all()
        )
        
        # Convert to BookBorrowed format
        user.borrowed_books = [
            BookBorrowed(
                id=record.book.id,
                title=record.book.title,
                borrower_name=f"{user.firstname} {user.lastname}",
                borrower_email=user.email,
                borrow_date=record.borrow_date,
                return_date=record.return_date
            ) for record in borrow_records
        ]
    
    return user


def get_users_with_borrowed_books(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get all users who have borrowed books.
    
    Args:
        db: Database session injected by FastAPI dependency system
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
    
    Returns:
        List of users who have borrowed books
    """
    # Get users who have borrow records
    users = (
        db.query(User)
        .join(BorrowRecord)
        .distinct()
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    # For each user, get their borrowed books
    for user in users:
        # Get all active borrow records for this user with book data
        borrow_records = (
            db.query(BorrowRecord)
            .filter(BorrowRecord.user_id == user.id)
            .join(BorrowRecord.book)
            .all()
        )
        
        # Convert to BookBorrowed format
        user.borrowed_books = [
            BookBorrowed(
                id=record.book.id,
                title=record.book.title,
                borrower_name=f"{user.firstname} {user.lastname}",
                borrower_email=user.email,
                borrow_date=record.borrow_date,
                return_date=record.return_date
            ) for record in borrow_records
        ]
    
    return users
