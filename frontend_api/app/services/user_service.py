from sqlalchemy.orm import Session
from ..models.user import User
from ..schemas.user import UserCreate
from shared.message_broker import MessageBroker
from shared.message_types import MessageType
from shared.exceptions import (
    LibraryException,
    DatabaseOperationError,
    ResourceNotFoundError,
    MessageBrokerError
)
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, message_broker: MessageBroker):
        self.message_broker = message_broker

    def get_user(self, db: Session, user_id: int):
        """Get a user by ID."""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ResourceNotFoundError("User", user_id)
            return user
        except ResourceNotFoundError:
            raise
        except SQLAlchemyError as e:
            raise DatabaseOperationError(f"Failed to fetch user: {str(e)}") from e
        except Exception as e:
            raise LibraryException(f"An unexpected error occurred while fetching user: {str(e)}")

    def get_user_by_email(self, db: Session, email: str):
        """Get a user by email."""
        try:
            return db.query(User).filter(User.email == email).first()
        except SQLAlchemyError as e:
            raise DatabaseOperationError(f"Failed to fetch user by email: {str(e)}") from e
        except Exception as e:
            raise LibraryException(f"An unexpected error occurred while fetching user by email: {str(e)}")

    async def create_user(self, db: Session, user: UserCreate) -> User:
        """Create a new user and notify admin_api."""
        try:
            # Check if user already exists
            try:
                db_user = self.get_user_by_email(db, email=user.email)
                if db_user:
                    return db_user
            except SQLAlchemyError as e:
                raise DatabaseOperationError(f"Failed to check existing user: {str(e)}") from e
                
            # Create new user
            db_user = User(
                email=user.email,
                firstname=user.firstname,
                lastname=user.lastname
            )

            try:
                db.add(db_user)
                db.commit()
                db.refresh(db_user)
            except SQLAlchemyError as e:
                db.rollback()
                raise DatabaseOperationError(f"Failed to create user: {str(e)}") from e

            # Notify admin_api about new user
            try:
                await self.message_broker.publish(
                    MessageType.USER_CREATED.value,
                    {
                        "email": db_user.email,
                        "firstname": db_user.firstname,
                        "lastname": db_user.lastname
                    }
                )
            except Exception as e:
                raise MessageBrokerError(f"Failed to publish user creation message: {str(e)}") from e
            
            return db_user
            
        except (DatabaseOperationError, MessageBrokerError):
            raise
        except Exception as e:
            raise LibraryException(f"An unexpected error occurred while creating user: {str(e)}")

# Create instance to be imported by other modules
message_broker = MessageBroker(settings.RABBITMQ_URL)
user_service = UserService(message_broker)
