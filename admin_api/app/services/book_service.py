from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.book import Book
from ..schemas.book import BookCreate, BookUpdate
from ..core.redis import publish_book_update


def create_books(db: Session, books: list[BookCreate]) -> list[Book]:
    """Add multiple books to the catalogue using bulk insert.
    
    Args:
        db: Database session injected by FastAPI dependency system
        books: List of book data validated by Pydantic
    
    Returns:
        List of created book instances
    """
    # Convert Pydantic models to dictionaries for bulk insert
    book_values = [book.model_dump() for book in books]
    
    # Bulk insert all books in a single statement
    result = db.execute(Book.__table__.insert().returning(Book), book_values)
    db.commit()
    
    # Get all inserted books
    inserted_books = result.fetchall()
    db_books = [Book(**dict(row)) for row in inserted_books]
    
    # Publish all updates to Redis in one go
    publish_book_updates(book_values, 'create')
    
    return db_books


def delete_book(db: Session, book_id: int) -> bool:
    """Delete a book from the catalogue.
    
    Args:
        db: Database session injected by FastAPI dependency system
        book_id: ID of the book to delete
    
    Returns:
        True if book was deleted, False if book was not found
    """
    book = db.query(Book).filter(Book.id == book_id).first()
    if book:
        # Publish to Redis for frontend service
        publish_book_update({'id': book_id}, 'delete')
        
        db.delete(book)
        db.commit()
        return True
    return False


def get_book(db: Session, book_id: int) -> Optional[Book]:
    """Get a book by its ID.
    
    Args:
        db: Database session injected by FastAPI dependency system
        book_id: ID of the book to retrieve
    
    Returns:
        Book instance if found, None otherwise
    """
    return db.query(Book).filter(Book.id == book_id).first()


def get_unavailable_books(db: Session, skip: int = 0, limit: int = 100) -> List[Book]:
    """Get all books that are currently borrowed, including their return dates and borrower info.
    
    Args:
        db: Database session injected by FastAPI dependency system
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
    
    Returns:
        List of unavailable books with their return dates and borrower information
    """
    # Get books that are currently borrowed by joining with borrow records and users
    return (
        db.query(Book)
        .join(Book.borrow_records)
        .join(BorrowRecord.user)
        .filter(Book.available == False)
        .offset(skip)
        .limit(limit)
        .all()
    )
