from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from ..models.book import Book
from ..schemas.book import BookResponse, BookDetail, BookCreate, BookList
from shared.message_types import MessageType
from shared.message_broker import MessageBroker
from shared.pagination import PaginatedResponse
from shared.exceptions import (
    LibraryException,
    DatabaseOperationError,
    ResourceNotFoundError,
    MessageBrokerError
)
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class BookService:
    def __init__(self, message_broker: MessageBroker):
        self.message_broker = message_broker

    def get_book(self, db: Session, book_id: int) -> Optional[BookDetail]:
        """Get a book by its ID."""
        try:
            book = db.query(Book).filter(Book.id == book_id).first()
            if not book or not book.available:
                raise ResourceNotFoundError("Book", book_id)
            
            return BookDetail.model_validate(book)
        except ResourceNotFoundError:
            raise
        except SQLAlchemyError as e:
            raise DatabaseOperationError(f"Failed to fetch book: {str(e)}") from e
        except Exception as e:
            raise LibraryException(f"An unexpected error occurred while fetching book: {str(e)}")

    def get_books(
        self,
        db: Session,
        page: int = 1,
        limit: int = 10,
        publisher: Optional[str] = None,
        category: Optional[str] = None,
        available_only: bool = True
    ) -> PaginatedResponse[BookList]:
        """Get books with optional filtering and pagination."""
        try:
            query = db.query(Book)
            if publisher:
                query = query.filter(Book.publisher == publisher)
            if category:
                query = query.filter(Book.category == category)
            if available_only:
                query = query.filter(Book.available == True)
            
            try:
                total = query.count()
            except SQLAlchemyError as e:
                raise DatabaseOperationError(f"Failed to count books: {str(e)}") from e
            
            if total == 0:
                return PaginatedResponse.create(
                    items=[],
                    total=0,
                    page=page,
                    limit=limit
                )
            
            skip = (page - 1) * limit
            
            try:
                books = (
                    query
                    .order_by(Book.title)
                    .offset(skip)
                    .limit(limit)
                    .all()
                )
            except SQLAlchemyError as e:
                raise DatabaseOperationError(f"Failed to fetch books: {str(e)}") from e
            
            book_responses = [BookList.model_validate(book) for book in books]
            
            return PaginatedResponse.create(
                items=book_responses,
                total=total,
                page=page,
                limit=limit
            )
            
        except (ResourceNotFoundError, DatabaseOperationError):
            raise
        except Exception as e:
            raise LibraryException(f"An unexpected error occurred while fetching books: {str(e)}")

    async def get_books_by_publisher(
        self, 
        db: Session, 
        publisher: str,
        page: int = 1,
        limit: int = 10
    ) -> PaginatedResponse[BookResponse]:
        """Get books filtered by publisher with pagination."""
        try:
            query = db.query(Book).filter(Book.publisher == publisher)
            
            try:
                total = query.count()
            except SQLAlchemyError as e:
                raise DatabaseOperationError(f"Failed to count books by publisher: {str(e)}") from e
            
            if total == 0:
                return PaginatedResponse.create(
                    items=[],
                    total=0,
                    page=page,
                    limit=limit
                )
            
            skip = (page - 1) * limit
            
            try:
                books = (
                    query
                    .order_by(Book.title)
                    .offset(skip)
                    .limit(limit)
                    .all()
                )
            except SQLAlchemyError as e:
                raise DatabaseOperationError(f"Failed to fetch books by publisher: {str(e)}") from e
            
            book_responses = [BookResponse.model_validate(book) for book in books]
            
            return PaginatedResponse.create(
                items=book_responses,
                total=total,
                page=page,
                limit=limit
            )
            
        except (ResourceNotFoundError, DatabaseOperationError):
            raise
        except Exception as e:
            raise LibraryException(f"An unexpected error occurred while fetching books by publisher: {str(e)}")

    async def get_books_by_category(
        self, 
        db: Session, 
        category: str,
        page: int = 1,
        limit: int = 10
    ) -> PaginatedResponse[BookResponse]:
        """Get books filtered by category with pagination."""
        try:
            query = db.query(Book).filter(Book.category == category)
            
            try:
                total = query.count()
            except SQLAlchemyError as e:
                raise DatabaseOperationError(f"Failed to count books by category: {str(e)}") from e
            
            if total == 0:
                return PaginatedResponse.create(
                    items=[],
                    total=0,
                    page=page,
                    limit=limit
                )
            
            skip = (page - 1) * limit
            
            try:
                books = (
                    query
                    .order_by(Book.title)
                    .offset(skip)
                    .limit(limit)
                    .all()
                )
            except SQLAlchemyError as e:
                raise DatabaseOperationError(f"Failed to fetch books by category: {str(e)}") from e
            
            book_responses = [BookResponse.model_validate(book) for book in books]
            
            return PaginatedResponse.create(
                items=book_responses,
                total=total,
                page=page,
                limit=limit
            )
            
        except (ResourceNotFoundError, DatabaseOperationError):
            raise
        except Exception as e:
            raise LibraryException(f"An unexpected error occurred while fetching books by category: {str(e)}")

    async def create_books(self, db: Session, books: List[BookCreate]) -> List[Book]:
        """Create multiple books in the frontend API."""
        try:
            db_books = []
            for book in books:
                book_data = book.model_dump()
                book_data['available'] = True
                
                try:
                    existing_book = db.query(Book).filter(Book.isbn == book_data['isbn']).first()
                except SQLAlchemyError as e:
                    raise DatabaseOperationError(f"Failed to check for existing book: {str(e)}") from e
                
                if existing_book:
                    logger.info(f"Book with ISBN {book_data['isbn']} already exists, skipping")
                    continue
                
                db_book = Book(**book_data)
                db.add(db_book)
                db_books.append(db_book)
            
            if db_books:
                try:
                    db.commit()
                except SQLAlchemyError as e:
                    db.rollback()
                    raise DatabaseOperationError(f"Failed to commit new books: {str(e)}") from e
            
            return db_books
            
        except SQLAlchemyError as e:
            raise LibraryException(
                message=f"An unexpected error occurred while creating books: {str(e)}",
                error_code="BOOK_CREATION_ERROR"
            )

    async def delete_book_by_isbn(self, db: Session, isbn: str) -> bool:
        """Delete a book by its ISBN."""
        try:
            try:
                db_book = db.query(Book).filter(Book.isbn == isbn).first()
            except SQLAlchemyError as e:
                raise DatabaseOperationError(f"Failed to fetch book for deletion: {str(e)}") from e
            
            if not db_book:
                raise ResourceNotFoundError("Book", isbn)
            
            try:
                db.delete(db_book)
                db.commit()
            except SQLAlchemyError as e:
                db.rollback()
                raise DatabaseOperationError(f"Failed to delete book: {str(e)}") from e
            
            return True
            
        except (ResourceNotFoundError, DatabaseOperationError):
            raise
        except Exception as e:
            raise LibraryException(f"An unexpected error occurred while deleting book: {str(e)}")

# Export the class
__all__ = ['BookService']
