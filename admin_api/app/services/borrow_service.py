from sqlalchemy.orm import Session
from datetime import date
from ..models.borrow import BorrowRecord
from ..models.book import Book
from ..models.user import User
from ..schemas.borrow import BorrowCreate
from shared.message_broker import MessageBroker
from shared.message_types import MessageType
from shared.exceptions import (
    LibraryException,
    DatabaseOperationError,
    ResourceNotFoundError,
    ValidationError
)
import logging
from ..core.config import settings
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

class BorrowService:
    def __init__(self, message_broker: MessageBroker):
        self.message_broker = message_broker

    async def create_borrow_record(self, db: Session, borrow_data: dict) -> BorrowRecord:
        """Create a new borrow record from frontend message using email and ISBN.
        
        Args:
            db: Database session
            borrow_data: Dictionary containing user_email, book_isbn, and return_date
            
        Returns:
            Created borrow record
        """
        try:
            # Find user by email
            try:
                user = db.query(User).filter(User.email == borrow_data["user_email"]).first()
                if not user:
                    raise ResourceNotFoundError("User", borrow_data["user_email"])
            except SQLAlchemyError as e:
                raise DatabaseOperationError(
                    message="Failed to fetch user from database"
                ) from e

            # Find book by ISBN
            try:
                book = db.query(Book).filter(Book.isbn == borrow_data["book_isbn"]).first()
                if not book:
                    raise ResourceNotFoundError("Book", borrow_data["book_isbn"])
            except SQLAlchemyError as e:
                raise DatabaseOperationError(
                    message="Failed to fetch book from database"
                ) from e

            # Check if book is available
            if not book.available:
                raise ValidationError(
                    message="Book is not available"
                )

            # Create borrow record
            db_borrow = BorrowRecord(
                user_id=user.id,
                book_id=book.id,
                borrow_date=date.today(),
                return_date=borrow_data["return_date"]
            )

            # Update book availability
            book.available = False
            book.current_borrower_id = user.id

            try:
                # Add both changes to the session
                db.add(db_borrow)
                db.add(book)
                db.commit()
                db.refresh(db_borrow)
                db.refresh(book)
                
                logger.info(f"Successfully created borrow record for book {book.isbn} and user {user.email}")
                return db_borrow

            except SQLAlchemyError as e:
                db.rollback()
                raise DatabaseOperationError(
                    message="Failed to create borrow record"
                ) from e

        except (ResourceNotFoundError, ValidationError, DatabaseOperationError):
            raise  # Re-raise these specific exceptions
        except Exception as e:
            raise LibraryException(
                message="Failed to process borrow request",
                error_code="BORROW_CREATION_ERROR"
            ) from e

# Create instance to be imported by other modules
message_broker = MessageBroker(settings.RABBITMQ_URL)
borrow_service = BorrowService(message_broker) 