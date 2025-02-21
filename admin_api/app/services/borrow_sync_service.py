from shared.message_types import MessageType
from shared.message_broker import MessageBroker
from .borrow_service import BorrowService
from ..core.database import SessionLocal
from ..schemas.borrow import BorrowCreate
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class BorrowSyncService:
    def __init__(self, message_broker: MessageBroker):
        self.message_broker = message_broker
        self.borrow_service = BorrowService(message_broker)

    async def start(self):
        """Initialize connections and start listening for messages"""
        logger.info("Starting BorrowSyncService...")
        await self.message_broker.connect()
        
        # Subscribe to borrow-related events
        logger.info(f"Subscribing to {MessageType.BOOK_BORROWED.value} events...")
        await self.message_broker.subscribe(
            MessageType.BOOK_BORROWED.value,
            self._handle_book_borrowed
        )
        logger.info("BorrowSyncService started and subscribed to borrow events")

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

    async def _handle_book_borrowed(self, data: dict):
        """Handle book borrow message from frontend_api"""
        logger.info(f"Received book borrow message with data: {data}")
        try:
            with self.get_db() as db:
                logger.info("Creating database session...")
                logger.info("Calling create_borrow_record...")
                borrow = await self.borrow_service.create_borrow_record(db, data)
                logger.info(f"Borrow record creation successful for book {data['book_isbn']}")
                return borrow
        except Exception as e:
            logger.error(f"Error in _handle_book_borrowed: {str(e)}", exc_info=True)
            raise