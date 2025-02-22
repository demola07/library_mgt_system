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

# Add shared directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from shared.message_types import MessageType
from shared.message_broker import MessageBroker

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
            
            # Convert Pydantic models to dictionaries for bulk insert
            book_values = [book.model_dump() for book in books]
            
            # Check for existing ISBNs first
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
                # Commit the transaction for new books
                db.commit()
                
                # Convert new books to dict format for message
                books_data = []
                for book in new_books:
                    book_dict = {
                        "title": book.title,
                        "author": book.author,
                        "isbn": book.isbn,
                        "publisher": book.publisher,
                        "category": book.category,
                        "available": True
                    }
                    books_data.append(book_dict)
                
                # Notify frontend_api about new books
                if books_data:
                    await self.message_broker.publish(
                        MessageType.BOOKS_CREATED.value,
                        books_data
                    )
                
                logger.info(f"Successfully created {len(new_books)} new books and notified frontend")
            
            # Return both new and existing books
            all_books = new_books + existing_books
            if not all_books:
                logger.warning("No books were created or found")
            else:
                logger.info(f"Returning {len(all_books)} books ({len(new_books)} new, {len(existing_books)} existing)")
            
            return all_books
            
        except Exception as e:
            db.rollback()
            error_msg = f"Failed to create books in admin API: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg)


    async def delete_book(self, db: Session, book_id: int) -> bool:
        """Delete a book from the catalogue.
        
        Args:
            db: Database session
            book_id: ID of the book to delete
        
        Returns:
            True if book was deleted, False if book was not found
        """
        db_book = self.get_book(db, book_id)
        if db_book:
            # Get the ISBN before deleting
            book_isbn = db_book.isbn
            
            db.delete(db_book)
            db.commit()
            
            # Notify frontend_api about deleted book using ISBN
            await self.message_broker.publish(
                MessageType.BOOK_DELETED.value,
                {"isbn": book_isbn}
            )
            
            logger.info(f"Successfully deleted book with ISBN {book_isbn}")
            return True
            
        logger.info(f"Book with ID {book_id} not found for deletion")
        return False

    def get_book(self, db: Session, book_id: int) -> Optional[Book]:
        """Get a book by its ID.
        
        Args:
            db: Database session
            book_id: ID of the book to retrieve
        
        Returns:
            Book instance if found, None otherwise
        """
        return db.query(Book).filter(Book.id == book_id).first()

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
            Paginated response containing unavailable books with their details
            
        Raises:
            ValueError: If there's an error retrieving the books
        """
        try:
            # Calculate skip
            skip = (page - 1) * limit
            
            # Base query for reuse
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
            
            # Get total count
            total = base_query.count()
            
            # Get paginated results
            results = (
                base_query
                .order_by(Book.id)
                .offset(skip)
                .limit(limit)
                .all()
            )
            
            # Transform to DTOs
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
            
        except Exception as e:
            logger.error("Failed to retrieve unavailable books", exc_info=True)
            raise ValueError(f"Error fetching unavailable books: {str(e)}") from e

# Create instance to be imported by other modules
message_broker = MessageBroker(settings.RABBITMQ_URL)
book_service = BookService(message_broker)
