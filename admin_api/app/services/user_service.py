from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.user import User
from ..models.borrow import BorrowRecord
from ..schemas.book import BookBorrowed
from shared.message_broker import MessageBroker
from shared.message_types import MessageType
from datetime import datetime
import logging
from shared.pagination import PaginatedResponse
from ..schemas.user import UserResponse, UserWithBorrowedBooksResponse

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, message_broker: MessageBroker):
        self.message_broker = message_broker

    async def get_users(
        self, 
        db: Session, 
        page: int = 1, 
        limit: int = 10
    ) -> PaginatedResponse[UserResponse]:
        """Get all users with pagination.
        
        Args:
            db: Database session
            page: Current page number (1-based)
            limit: Maximum number of items per page
            
        Returns:
            Paginated response containing users
            
        Raises:
            ValueError: If there's an error retrieving users
        """
        try:
            # Calculate skip
            skip = (page - 1) * limit
            
            # Base query for reuse
            base_query = db.query(User)
            
            # Get total count
            total = base_query.count()
            
            # Get paginated results
            users = (
                base_query
                .order_by(User.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
            
            # Convert to response schema
            user_responses = [UserResponse.model_validate(user) for user in users]
            
            return PaginatedResponse.create(
                items=user_responses,
                total=total,
                page=page,
                limit=limit
            )
            
        except Exception as e:
            error_msg = f"Failed to get users: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg)

    async def get_users_with_borrowed_books(
        self, 
        db: Session, 
        page: int = 1,
        limit: int = 10
    ) -> PaginatedResponse[UserWithBorrowedBooksResponse]:
        """Get all users who have borrowed books with pagination.
        
        Args:
            db: Database session
            page: Current page number (1-based)
            limit: Maximum number of items per page
            
        Returns:
            Paginated response containing users with their borrowed books
            
        Raises:
            ValueError: If there's an error retrieving the data
        """
        try:
            # Calculate skip
            skip = (page - 1) * limit
            
            # Base query for users with borrow records
            base_query = (
                db.query(User)
                .join(BorrowRecord)
                .distinct()
            )
            
            # Get total count
            total = base_query.count()
            
            # Get paginated results
            users = (
                base_query
                .order_by(User.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
            
            # For each user, get their borrowed books
            for user in users:
                borrow_records = (
                    db.query(BorrowRecord)
                    .filter(BorrowRecord.user_id == user.id)
                    .join(BorrowRecord.book)
                    .all()
                )
                
                # Convert to BookBorrowed format
                user.borrowed_books = [
                    self._create_book_borrowed_dto(record, user)
                    for record in borrow_records
                ]
            
            # Convert to response schema
            user_responses = [
                UserWithBorrowedBooksResponse.model_validate(user) 
                for user in users
            ]
            
            return PaginatedResponse.create(
                items=user_responses,
                total=total,
                page=page,
                limit=limit
            )
            
        except Exception as e:
            error_msg = f"Failed to get users with borrowed books: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg)

    def _create_book_borrowed_dto(
        self, 
        borrow_record: BorrowRecord, 
        user: User
    ) -> BookBorrowed:
        """Helper method to create BookBorrowed DTO from a borrow record.
        
        Args:
            borrow_record: The borrow record to convert
            user: The user who borrowed the book
        
        Returns:
            BookBorrowed DTO
        """
        return BookBorrowed(
            id=borrow_record.book.id,
            title=borrow_record.book.title,
            author=borrow_record.book.author,
            isbn=borrow_record.book.isbn,
            publisher=borrow_record.book.publisher,
            category=borrow_record.book.category,
            borrow_date=borrow_record.borrow_date,
            return_date=borrow_record.return_date
        )

    async def create_user_from_frontend(self, db: Session, user_data: dict) -> User:
        """Create a new user from frontend_api message."""
        try:
            logger.info(f"Starting user creation in admin API with data: {user_data}")
            
            # Check if user already exists
            existing_user = self.get_user_by_email(db, user_data["email"])
            logger.info(f"Checked for existing user: {'Found' if existing_user else 'Not found'}")
            
            if existing_user:
                logger.info(f"User already exists in admin API: {user_data['email']}")
                return existing_user
            
            # Create user in database
            logger.info("Creating new user object...")
            db_user = User(
                email=user_data["email"],
                firstname=user_data["firstname"],
                lastname=user_data["lastname"],
                created_at=datetime.utcnow()
            )
            
            logger.info("Adding user to database session...")
            db.add(db_user)
            
            logger.info("Committing transaction...")
            db.commit()
            
            logger.info("Refreshing user object...")
            db.refresh(db_user)
            
            logger.info(f"Successfully created user in admin API: {db_user.email}")
            return db_user
            
        except KeyError as e:
            error_msg = f"Missing required field in user data: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Failed to create user in admin API: {str(e)}"
            logger.error(error_msg, exc_info=True)
            db.rollback()
            raise ValueError(error_msg)

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get a user by email."""
        try:
            return db.query(User).filter(User.email == email).first()
        except Exception as e:
            logger.error(f"Error querying user by email: {str(e)}", exc_info=True)
            raise

# Create instance to be imported by other modules
message_broker = MessageBroker("amqp://guest:guest@rabbitmq:5672/")
user_service = UserService(message_broker)
