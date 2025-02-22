from shared.message_types import MessageType
from shared.message_broker import MessageBroker
from .book_service import BookService
from ..core.database import SessionLocal
from ..schemas.book import BookCreate
from contextlib import contextmanager
import logging
from ..core.config import settings
from shared.exceptions import (
    LibraryException,
    MessageBrokerError,
    DatabaseOperationError
)

logger = logging.getLogger(__name__)

class BookSyncService:
    def __init__(self):
        self.message_broker = MessageBroker(settings.RABBITMQ_URL)
        self.book_service = BookService(self.message_broker)

    async def start(self):
        """Initialize connections and start listening for messages"""
        try:
            logger.info("Starting BookSyncService...")
            await self.message_broker.connect()
            
            await self.message_broker.subscribe(
                MessageType.BOOKS_CREATED.value,
                self._handle_books_created
            )
            await self.message_broker.subscribe(
                MessageType.BOOK_DELETED.value,
                self._handle_book_deleted
            )
            logger.info("BookSyncService started and subscribed to book events")
        except Exception as e:
            raise MessageBrokerError(f"Failed to start BookSyncService: {str(e)}")

    async def stop(self):
        """Cleanup connections"""
        try:
            if self.message_broker.connection:
                await self.message_broker.connection.close()
        except Exception as e:
            raise MessageBrokerError(f"Failed to stop BookSyncService: {str(e)}")

    @contextmanager
    def get_db(self):
        """Get database session with context management."""
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    async def _handle_books_created(self, data: list):
        """Handle multiple books creation message from admin_api"""
        try:
            with self.get_db() as db:
                books = [BookCreate(**book_data) for book_data in data]
                await self.book_service.create_books(db, books)
        except Exception as e:
            # Log but don't raise - we don't want to crash the message consumer
            logger.error(f"Error processing books creation message: {str(e)}", exc_info=True)

    async def _handle_book_deleted(self, data: dict):
        """Handle book deletion message from admin_api"""
        try:
            with self.get_db() as db:
                await self.book_service.delete_book_by_isbn(db, data["isbn"])
        except Exception as e:
            # Log but don't raise - we don't want to crash the message consumer
            logger.error(f"Error processing book deletion message: {str(e)}", exc_info=True)

# Create a singleton instance to be used throughout the application
book_sync_service = BookSyncService()

# Export the instance
__all__ = ['book_sync_service'] 