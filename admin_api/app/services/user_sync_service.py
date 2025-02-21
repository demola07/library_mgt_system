from shared.message_types import MessageType
from shared.message_broker import MessageBroker
from .user_service import UserService
from ..core.database import SessionLocal
from ..schemas.user import UserCreate
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class UserSyncService:
    def __init__(self, message_broker: MessageBroker):
        self.message_broker = message_broker
        self.user_service = UserService(message_broker)

    async def start(self):
        """Initialize connections and start listening for messages"""
        logger.info("Starting UserSyncService...")
        await self.message_broker.connect()
        
        # Subscribe to user-related events
        logger.info(f"Subscribing to {MessageType.USER_CREATED.value} events...")
        await self.message_broker.subscribe(
            MessageType.USER_CREATED.value,
            self._handle_user_created
        )
        logger.info("UserSyncService started and subscribed to user events")

    async def stop(self):
        """Cleanup connections"""
        if self.message_broker.connection:
            await self.message_broker.connection.close()

    @contextmanager
    def get_db(self):
        """Get database session with context management."""
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    async def _handle_user_created(self, data: dict):
        """Handle user creation message from frontend_api"""
        logger.info(f"Received user creation message with data: {data}")
        try:
            with self.get_db() as db:
                logger.info("Creating database session...")
                logger.info("Calling create_user_from_frontend...")
                user = await self.user_service.create_user_from_frontend(db, data)
                logger.info(f"User creation successful: {user.email if user else 'No user returned'}")
                return user
        except Exception as e:
            logger.error(f"Error in _handle_user_created: {str(e)}", exc_info=True)
            raise 