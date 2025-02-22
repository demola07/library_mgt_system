from shared.message_types import MessageType
from shared.message_broker import MessageBroker
from .book_service import BookService
from ..core.database import SessionLocal
from ..schemas.book import BookCreate
from contextlib import contextmanager
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)

class BookSyncService:
    def __init__(self):
        self.message_broker = MessageBroker(settings.RABBITMQ_URL)
        self.book_service = BookService(self.message_broker)

    async def start(self):
        """Initialize connections and start listening for messages"""
        await self.message_broker.connect()
        
        # Subscribe to book-related events
        await self.message_broker.subscribe(MessageType.BOOKS_CREATED.value, self._handle_books_created)
        await self.message_broker.subscribe(MessageType.BOOK_DELETED.value, self._handle_book_deleted)
        logger.info("BookSyncService started and subscribed to book events")

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

    async def _handle_books_created(self, data: list):
        """Handle multiple books creation message from admin_api"""
        logger.info(f"Received books creation message with {len(data)} books")
        try:
            with self.get_db() as db:
                # Convert each book data to BookCreate
                books = [BookCreate(**book_data) for book_data in data]
                await self.book_service.create_books(db, books)
                logger.info(f"Successfully created {len(books)} books in frontend API")
        except Exception as e:
            logger.error(f"Error creating books in frontend API: {str(e)}", exc_info=True)
            raise

    async def _handle_book_deleted(self, data: dict):
        """Handle book deletion message from admin_api"""
        logger.info(f"Received book deletion message for ISBN {data['isbn']}")
        try:
            with self.get_db() as db:
                success = await self.book_service.delete_book_by_isbn(db, data["isbn"])
                if success:
                    logger.info(f"Successfully deleted book with ISBN {data['isbn']}")
                else:
                    logger.warning(f"Book with ISBN {data['isbn']} not found for deletion")
        except Exception as e:
            logger.error(f"Error deleting book in frontend API: {str(e)}", exc_info=True)
            raise

# Create a singleton instance to be used throughout the application
book_sync_service = BookSyncService()

# Export the instance
__all__ = ['book_sync_service'] 