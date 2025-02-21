from sqlalchemy.orm import Session
from datetime import date
from ..models.borrow import BorrowRecord
from ..models.book import Book
from ..models.user import User
from ..schemas.borrow import BorrowCreate
from shared.message_broker import MessageBroker
from shared.message_types import MessageType
import logging

logger = logging.getLogger(__name__)

class BorrowService:
    def __init__(self, message_broker: MessageBroker):
        self.message_broker = message_broker

    async def create_borrow_record(self, db: Session, borrow_data: dict) -> BorrowRecord:
        """Create a new borrow record from frontend message using email and ISBN."""
        try:
            # Find user by email
            user = db.query(User).filter(User.email == borrow_data["user_email"]).first()
            if not user:
                raise ValueError(f"User with email {borrow_data['user_email']} not found")

            # Find book by ISBN
            book = db.query(Book).filter(Book.isbn == borrow_data["book_isbn"]).first()
            if not book:
                raise ValueError(f"Book with ISBN {borrow_data['book_isbn']} not found")

            # Check if book is available
            if not book.available:
                raise ValueError(f"Book with ISBN {borrow_data['book_isbn']} is not available")

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

            except Exception as e:
                db.rollback()
                error_msg = f"Failed to create borrow record in admin_api: {str(e)}"
                logger.error(error_msg)
                raise ValueError(error_msg)

        except Exception as e:
            error_msg = f"Error in create_borrow_record: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

# Create instance to be imported by other modules
message_broker = MessageBroker("amqp://guest:guest@rabbitmq:5672/")
borrow_service = BorrowService(message_broker) 