from sqlalchemy.orm import Session
from datetime import date, timedelta
from ..models.borrow import BorrowRecord
from ..schemas.borrow import BorrowCreate
import sys
import os

# Add shared directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from ..models.book import Book
from ..models.user import User
from shared.message_types import MessageType
from shared.message_broker import MessageBroker

class BorrowService:
    def __init__(self, message_broker: MessageBroker):
        self.message_broker = message_broker

    async def create_borrow_record(self, db: Session, borrow: BorrowCreate) -> BorrowRecord:
        """Create a new borrow record and notify admin_api."""
        # Calculate return date
        return_date = date.today() + timedelta(days=borrow.days)
        
        # Get user and book details for the message
        user = db.query(User).filter(User.id == borrow.user_id).first()
        book = db.query(Book).filter(Book.id == borrow.book_id).first()
        
        if not user or not book:
            raise ValueError("User or book not found")
        
        # Create borrow record
        db_borrow = BorrowRecord(
            user_id=borrow.user_id,
            book_id=borrow.book_id,
            borrow_date=date.today(),
            return_date=return_date
        )
        
        # Update book availability
        if not book.available:
            raise ValueError(f"Book {book.title} is not available")
        
        book.available = False
        
        try:
            db.add(db_borrow)
            db.add(book)
            db.commit()
            db.refresh(db_borrow)
            db.refresh(book)
            
            # Notify admin_api about borrowed book using email and ISBN
            await self.message_broker.publish(
                MessageType.BOOK_BORROWED.value,
                {
                    "book_isbn": book.isbn,
                    "user_email": user.email,
                    "return_date": return_date.isoformat()
                }
            )
            
            return db_borrow
            
        except Exception as e:
            db.rollback()
            raise ValueError(f"Failed to create borrow record: {str(e)}")
