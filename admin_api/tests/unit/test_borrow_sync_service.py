import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.borrow_sync_service import BorrowSyncService
from app.models.book import Book
from app.models.user import User
from app.models.borrow import BorrowRecord
from sqlalchemy.orm import Session
from datetime import datetime, date
from shared.message_types import MessageType

class TestBorrowSyncService:
    @pytest.fixture
    def mock_message_broker(self):
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_start_service(self, mock_message_broker):
        # Create service instance
        sync_service = BorrowSyncService(mock_message_broker)
        
        # Start service
        await sync_service.start()
        
        # Verify message broker was started and subscribed
        mock_message_broker.connect.assert_called_once()
        mock_message_broker.subscribe.assert_called_once_with(
            MessageType.BOOK_BORROWED.value,
            sync_service._handle_book_borrowed
        )

    @pytest.mark.asyncio
    async def test_stop_service(self, mock_message_broker):
        # Create service instance
        sync_service = BorrowSyncService(mock_message_broker)
        
        # Mock connection
        mock_message_broker.connection = AsyncMock()
        
        # Stop service
        await sync_service.stop()
        
        # Verify connection was closed
        mock_message_broker.connection.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_book_borrowed(self, db_session: Session, mock_message_broker):
        # Create service instance
        sync_service = BorrowSyncService(mock_message_broker)
        
        # Mock the get_db context manager
        mock_db_context = MagicMock()
        mock_db_context.__enter__ = MagicMock(return_value=db_session)
        mock_db_context.__exit__ = MagicMock(return_value=None)
        sync_service.get_db = MagicMock(return_value=mock_db_context)
        
        # Create test user and book
        user = User(email="test@example.com", firstname="Test", lastname="User")
        book = Book(
            title="Test Book",
            author="Test Author",
            isbn="123-456-789",
            publisher="Test Publisher",
            category="Test Category",
            available=True
        )
        db_session.add(user)
        db_session.add(book)
        db_session.commit()
        
        # Test borrow data with proper date object
        return_date = date.today()  # or a specific date
        borrow_data = {
            "user_email": "test@example.com",
            "book_isbn": "123-456-789",
            "return_date": return_date  # Use date object instead of ISO string
        }
        
        # Handle book borrowed message
        await sync_service._handle_book_borrowed(borrow_data)
        
        # Verify borrow record was created
        borrow_record = db_session.query(BorrowRecord).first()
        assert borrow_record is not None
        assert borrow_record.user_id == user.id
        assert borrow_record.book_id == book.id 