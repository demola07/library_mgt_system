from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.book import Book
from ..models.borrow import BorrowRecord
from ..schemas.book import BookCreate, UnavailableBook
from ..schemas.borrow import BookBorrowed
import sys
import os
import logging
from datetime import datetime
from sqlalchemy.orm import joinedload
from shared.pagination import PaginatedResponse
from sqlalchemy import or_
from ..core.config import settings
from shared.exceptions import ResourceNotFoundError, DatabaseOperationError
from sqlalchemy.exc import SQLAlchemyError
from shared.message_types import MessageType
from shared.message_broker import MessageBroker
from shared.exceptions import LibraryException
from shared.exceptions import MessageBrokerError

# Add shared directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

logger = logging.getLogger(__name__)

class BookService:
    def __init__(self, message_broker: MessageBroker):
        self.message_broker = message_broker

    async def create_books(self, db: Session, books: List[BookCreate]) -> List[Book]:
        """Add multiple books to the catalogue using bulk insert.
        
        Args:
            db: Database session
            books: List of book data validated by Pydantic
        
        Returns:
            List of created book instances
        """
        try:
            logger.info(f"Creating {len(books)} books in admin API")
            
            book_values = [book.model_dump() for book in books]
            new_books = []
            existing_books = []
            
            for book_data in book_values:
                existing_book = db.query(Book).filter(Book.isbn == book_data['isbn']).first()
                if existing_book:
                    logger.info(f"Book with ISBN {book_data['isbn']} already exists, skipping")
                    existing_books.append(existing_book)
                else:
                    db_book = Book(**book_data)
                    db.add(db_book)
                    new_books.append(db_book)
            
            if new_books:
                try:
                    db.commit()
                except SQLAlchemyError as e:
                    db.rollback()
                    raise DatabaseOperationError(
                        message="Failed to commit new books to database"
                    ) from e
                
                books_data = [
                    {
                        "title": book.title,
                        "author": book.author,
                        "isbn": book.isbn,
                        "publisher": book.publisher,
                        "category": book.category,
                        "available": True
                    }
                    for book in new_books
                ]
                
                try:
                    await self.message_broker.publish(
                        MessageType.BOOKS_CREATED.value,
                        books_data
                    )
                except Exception as e:
                    raise MessageBrokerError(
                        message="Failed to publish books created message"
                    ) from e
                
                logger.info(f"Successfully created {len(new_books)} new books and notified frontend")
            
            all_books = new_books + existing_books
            if not all_books:
                logger.warning("No books were created or found")
            
            return all_books
            
        except (DatabaseOperationError, MessageBrokerError):
            raise  # Re-raise these specific exceptions
        except Exception as e:
            raise LibraryException(
                message="Failed to process book creation",
                error_code="BOOK_CREATION_ERROR"
            ) from e

    async def delete_book(self, db: Session, book_id: int) -> bool:
        """Delete a book from the catalogue.
        
        Args:
            db: Database session
            book_id: ID of the book to delete
        
        Returns:
            True if book was deleted, False if book was not found
        """
        try:
            book = self.get_book(db, book_id)
            book_isbn = book.isbn
            
            db.delete(book)
            db.commit()
            
            await self.message_broker.publish(
                MessageType.BOOK_DELETED.value,
                {"isbn": book_isbn}
            )
            return True
            
        except ResourceNotFoundError:
            raise  # Re-raise as is
        except SQLAlchemyError as e:
            raise DatabaseOperationError(
                message="Failed to delete book",
                details={"book_id": book_id}
            ) from e
        except Exception as e:
            raise LibraryException(
                message="Failed to process book deletion",
                error_code="BOOK_DELETION_ERROR",
                details={"book_id": book_id}
            ) from e

    def get_book(self, db: Session, book_id: int) -> Book:
        """Get a book by its ID.
        
        Args:
            db: Database session
            book_id: ID of the book to retrieve
        
        Returns:
            Book instance if found
        """
        try:
            book = db.query(Book).filter(Book.id == book_id).first()
            if not book:
                raise ResourceNotFoundError("Book", book_id)
            return book
        except ResourceNotFoundError:
            raise  # Re-raise as is
        except SQLAlchemyError as e:
            raise DatabaseOperationError(
                message="Failed to fetch book from database",
                details={"book_id": book_id}
            ) from e
        except Exception as e:
            raise LibraryException(
                message="Failed to process book retrieval",
                error_code="BOOK_RETRIEVAL_ERROR",
                details={"book_id": book_id}
            ) from e

    async def get_unavailable_books(
        self, 
        db: Session, 
        page: int = 1,
        limit: int = 10
    ) -> PaginatedResponse[UnavailableBook]:
        """Retrieve all currently unavailable books with pagination.
        
        Args:
            db: Database session for executing queries
            page: Current page number (1-based)
            limit: Maximum number of items per page
        
        Returns:
            Paginated response containing unavailable books
        """
        try:
            skip = (page - 1) * limit
            
            base_query = (
                db.query(
                    Book,
                    BorrowRecord.borrow_date,
                    BorrowRecord.return_date
                )
                .filter(Book.available == False)
                .outerjoin(BorrowRecord)
                .filter(or_(
                    BorrowRecord.return_date > datetime.now(),
                    BorrowRecord.id == None
                ))
            )
            
            try:
                total = base_query.count()
                results = (
                    base_query
                    .order_by(Book.id)
                    .offset(skip)
                    .limit(limit)
                    .all()
                )
            except SQLAlchemyError as e:
                raise DatabaseOperationError(
                    message="Failed to fetch unavailable books"
                ) from e
            
            items = [
                UnavailableBook(
                    id=result.Book.id,
                    title=result.Book.title,
                    author=result.Book.author,
                    isbn=result.Book.isbn,
                    publisher=result.Book.publisher,
                    category=result.Book.category,
                    available=result.Book.available,
                    borrow_date=result.borrow_date,
                    return_date=result.return_date
                )
                for result in results
            ]
            
            return PaginatedResponse.create(
                items=items,
                total=total,
                page=page,
                limit=limit
            )
            
        except DatabaseOperationError:
            raise  # Re-raise as is
        except Exception as e:
            raise LibraryException(
                message="Failed to process unavailable books retrieval",
                error_code="BOOK_RETRIEVAL_ERROR"
            ) from e

# Create instance to be imported by other modules
message_broker = MessageBroker(settings.RABBITMQ_URL)
book_service = BookService(message_broker)
