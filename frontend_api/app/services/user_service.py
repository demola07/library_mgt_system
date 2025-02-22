from sqlalchemy.orm import Session
from ..models.user import User
from ..schemas.user import UserCreate
from shared.message_broker import MessageBroker
from shared.message_types import MessageType
from ..core.config import settings

class UserService:
    def __init__(self, message_broker: MessageBroker):
        self.message_broker = message_broker

    def get_user(self, db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    async def create_user(self, db: Session, user: UserCreate) -> User:
        """Create a new user and notify admin_api."""
        # Check if user already exists
        db_user = self.get_user_by_email(db, email=user.email)
        if db_user:
            return db_user
            
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
            print("User created successfully", db_user);
            # Notify admin_api about new user
            await self.message_broker.publish(
                MessageType.USER_CREATED.value,
                {
                    "email": db_user.email,
                    "firstname": db_user.firstname,
                    "lastname": db_user.lastname
                }
            )
            
            return db_user
            
        except Exception as e:
            db.rollback()
            raise ValueError(f"Failed to create user: {str(e)}")

# Create instance to be imported by other modules
message_broker = MessageBroker(settings.RABBITMQ_URL)
user_service = UserService(message_broker)
