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
from ..core.config import settings
from shared.exceptions import (
    LibraryException,
    DatabaseOperationError,
    ResourceNotFoundError,
    ValidationError
)
from sqlalchemy.exc import SQLAlchemyError

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
        """
        try:
            skip = (page - 1) * limit
            base_query = db.query(User)
            
            try:
                total = base_query.count()
                users = (
                    base_query
                    .order_by(User.created_at.desc())
                    .offset(skip)
                    .limit(limit)
                    .all()
                )
            except SQLAlchemyError as e:
                raise DatabaseOperationError(
                    message=f"Failed to fetch users: {str(e)}"
                ) from e
            
            user_responses = [UserResponse.model_validate(user) for user in users]
            
            return PaginatedResponse.create(
                items=user_responses,
                total=total,
                page=page,
                limit=limit
            )
            
        except DatabaseOperationError:
            raise  # Re-raise as is
        except Exception as e:
            raise LibraryException(
                message=f"An unexpected error occurred while fetching users: {str(e)}",
                error_code="USER_RETRIEVAL_ERROR"
            ) from e

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
        """
        try:
            skip = (page - 1) * limit
            
            base_query = (
                db.query(User)
                .join(BorrowRecord)
                .distinct()
            )
            
            try:
                total = base_query.count()
                users = (
                    base_query
                    .order_by(User.created_at.desc())
                    .offset(skip)
                    .limit(limit)
                    .all()
                )
            except SQLAlchemyError as e:
                raise DatabaseOperationError(
                    message="Failed to fetch users with borrowed books"
                ) from e
            
            for user in users:
                try:
                    borrow_records = (
                        db.query(BorrowRecord)
                        .filter(BorrowRecord.user_id == user.id)
                        .join(BorrowRecord.book)
                        .all()
                    )
                except SQLAlchemyError as e:
                    raise DatabaseOperationError(
                        message="Failed to fetch borrow records"
                    ) from e
                
                user.borrowed_books = [
                    self._create_book_borrowed_dto(record, user)
                    for record in borrow_records
                ]
            
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
            
        except DatabaseOperationError:
            raise  # Re-raise as is
        except Exception as e:
            raise LibraryException(
                message="Failed to process users with borrowed books retrieval",
                error_code="USER_BORROWED_BOOKS_ERROR"
            ) from e

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
            
            try:
                existing_user = self.get_user_by_email(db, user_data["email"])
            except KeyError as e:
                raise ValidationError(
                    message=f"Missing required field: {str(e)}"
                )
            except SQLAlchemyError as e:
                raise DatabaseOperationError(
                    message=f"Failed to check for existing user: {str(e)}"
                ) from e
            
            if existing_user:
                logger.info(f"User already exists in admin API: {user_data['email']}")
                return existing_user
            
            try:
                db_user = User(
                    email=user_data["email"],
                    firstname=user_data["firstname"],
                    lastname=user_data["lastname"],
                    created_at=datetime.utcnow()
                )
                
                db.add(db_user)
                db.commit()
                db.refresh(db_user)
                
                return db_user
                
            except SQLAlchemyError as e:
                db.rollback()
                raise LibraryException(
                    message=f"An unexpected error occurred while creating user: {str(e)}",
                    error_code="USER_CREATION_ERROR"
                )
            
        except (ValidationError, DatabaseOperationError):
            raise
        except Exception as e:
            raise LibraryException(
                message=f"An unexpected error occurred while creating user: {str(e)}",
                error_code="USER_CREATION_ERROR"
            ) from e

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get a user by email."""
        try:
            return db.query(User).filter(User.email == email).first()
        except SQLAlchemyError as e:
            raise LibraryException(
                message=f"An unexpected error occurred while fetching user by email: {str(e)}",
                error_code="USER_FETCH_ERROR"
            )

# Create instance to be imported by other modules
message_broker = MessageBroker(settings.RABBITMQ_URL)
user_service = UserService(message_broker)
