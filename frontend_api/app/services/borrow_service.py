from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import date, timedelta
from ..models.borrow import BorrowRecord
from ..schemas.borrow import BorrowCreate
from shared.message_types import MessageType
from shared.message_broker import MessageBroker
from shared.exceptions import (
    LibraryException,
    DatabaseOperationError,
    ResourceNotFoundError,
    ValidationError,
    MessageBrokerError
)
from ..models.book import Book
from ..models.user import User
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)

class BorrowService:
    def __init__(self, message_broker: MessageBroker):
        self.message_broker = message_broker

    async def create_borrow_record(self, db: Session, borrow: BorrowCreate) -> BorrowRecord:
        """Create a new borrow record and notify admin_api."""
        try:
            # Get user and book details
            try:
                user = db.query(User).filter(User.id == borrow.user_id).first()
                if not user:
                    raise ResourceNotFoundError("User", borrow.user_id)

                book = db.query(Book).filter(Book.id == borrow.book_id).first()
                if not book:
                    raise ResourceNotFoundError("Book", borrow.book_id)
            except SQLAlchemyError as e:
                raise DatabaseOperationError(f"Failed to fetch user or book: {str(e)}") from e

            # Validate book availability
            if not book.available:
                raise ValidationError(f"Book {book.title} is not available")

            # Calculate return date
            return_date = date.today() + timedelta(days=borrow.days)

            # Create borrow record
            try:
                db_borrow = BorrowRecord(
                    user_id=borrow.user_id,
                    book_id=borrow.book_id,
                    borrow_date=date.today(),
                    return_date=return_date
                )
                
                # Update book availability
                book.available = False
                
                db.add(db_borrow)
                db.add(book)
                db.commit()
                db.refresh(db_borrow)
                db.refresh(book)
            except SQLAlchemyError as e:
                db.rollback()
                raise DatabaseOperationError(f"Failed to create borrow record: {str(e)}") from e

            # Notify admin_api
            try:
                await self.message_broker.publish(
                    MessageType.BOOK_BORROWED.value,
                    {
                        "book_isbn": book.isbn,
                        "user_email": user.email,
                        "return_date": return_date.isoformat()
                    }
                )
            except Exception as e:
                raise MessageBrokerError(f"Failed to publish borrow message: {str(e)}") from e

            return db_borrow

        except (ResourceNotFoundError, ValidationError, DatabaseOperationError, MessageBrokerError):
            raise
        except Exception as e:
            raise LibraryException(
                message=f"An unexpected error occurred while creating borrow record: {str(e)}",
                error_code="UNEXPECTED_ERROR"
            )

# Create instance to be imported by other modules
message_broker = MessageBroker(settings.RABBITMQ_URL)
borrow_service = BorrowService(message_broker)
