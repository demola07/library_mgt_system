from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from ..models.book import Book
from ..schemas.book import BookResponse, BookDetail, BookCreate, BookList
from shared.message_types import MessageType
from shared.message_broker import MessageBroker
from shared.pagination import PaginatedResponse
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
                return None
            
            return BookDetail.model_validate(book)
        except Exception as e:
            logger.error(f"Error fetching book: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to fetch book: {str(e)}")

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
            
            total = query.count()
            
            # Return empty paginated response if no books found
            if total == 0:
                return PaginatedResponse.create(
                    items=[],
                    total=0,
                    page=page,
                    limit=limit
                )
            
            skip = (page - 1) * limit
            
            books = (
                query
                .order_by(Book.title)
                .offset(skip)
                .limit(limit)
                .all()
            )
            
            book_responses = [BookList.model_validate(book) for book in books]
            
            return PaginatedResponse.create(
                items=book_responses,
                total=total,
                page=page,
                limit=limit
            )
            
        except Exception as e:
            logger.error(f"Error fetching books: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to fetch books: {str(e)}")

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
            total = query.count()
            
            # Return empty paginated response if no books found
            if total == 0:
                return PaginatedResponse.create(
                    items=[],
                    total=0,
                    page=page,
                    limit=limit
                )
            
            skip = (page - 1) * limit
            
            books = (
                query
                .order_by(Book.title)
                .offset(skip)
                .limit(limit)
                .all()
            )
            
            book_responses = [BookResponse.model_validate(book) for book in books]
            
            return PaginatedResponse.create(
                items=book_responses,
                total=total,
                page=page,
                limit=limit
            )
            
        except Exception as e:
            logger.error(f"Error fetching books by publisher: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to fetch books by publisher: {str(e)}")

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
            total = query.count()
            
            # Return empty paginated response if no books found
            if total == 0:
                return PaginatedResponse.create(
                    items=[],
                    total=0,
                    page=page,
                    limit=limit
                )
            
            skip = (page - 1) * limit
            
            books = (
                query
                .order_by(Book.title)
                .offset(skip)
                .limit(limit)
                .all()
            )
            
            book_responses = [BookResponse.model_validate(book) for book in books]
            
            return PaginatedResponse.create(
                items=book_responses,
                total=total,
                page=page,
                limit=limit
            )
            
        except Exception as e:
            logger.error(f"Error fetching books by category: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to fetch books by category: {str(e)}")

    async def create_books(self, db: Session, books: List[BookCreate]) -> List[Book]:
        """Create multiple books in the frontend API.
        
        Args:
            db: Database session
            books: List of BookCreate objects
            
        Returns:
            List of created Book objects
        """
        try:
            logger.info(f"Creating {len(books)} books in frontend API")
            
            # Create Book instances
            db_books = []
            for book in books:
                book_data = book.model_dump()
                book_data['available'] = True
                
                # Check if book with ISBN already exists
                existing_book = db.query(Book).filter(Book.isbn == book_data['isbn']).first()
                if existing_book:
                    logger.info(f"Book with ISBN {book_data['isbn']} already exists, skipping")
                    continue
                
                db_book = Book(**book_data)
                db.add(db_book)
                db_books.append(db_book)
            
            if db_books:
                # Commit the transaction
                db.commit()
                logger.info(f"Successfully created {len(db_books)} new books in frontend API")
            else:
                logger.info("No new books to create")
            
            return db_books
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating books in frontend API: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to create books: {str(e)}")

    async def delete_book_by_isbn(self, db: Session, isbn: str) -> bool:
        """Delete a book by its ISBN.
        
        Args:
            db: Database session
            isbn: ISBN of the book to delete
        
        Returns:
            True if book was deleted, False if book was not found
        """
        try:
            db_book = db.query(Book).filter(Book.isbn == isbn).first()
            if db_book:
                db.delete(db_book)
                db.commit()
                logger.info(f"Successfully deleted book with ISBN {isbn}")
                return True
                
            logger.info(f"Book with ISBN {isbn} not found for deletion")
            return False
            
        except Exception as e:
            db.rollback()
            error_msg = f"Failed to delete book: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg)

# Export the class
__all__ = ['BookService']
