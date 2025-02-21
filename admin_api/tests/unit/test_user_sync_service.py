import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.user_sync_service import UserSyncService
from app.models.user import User
from sqlalchemy.orm import Session
from shared.message_types import MessageType

class TestUserSyncService:
    @pytest.fixture
    def mock_message_broker(self):
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_start_service(self, mock_message_broker):
        # Create service instance
        sync_service = UserSyncService(mock_message_broker)
        
        # Start service
        await sync_service.start()
        
        # Verify message broker was started and subscribed
        mock_message_broker.connect.assert_called_once()
        mock_message_broker.subscribe.assert_called_once_with(
            MessageType.USER_CREATED.value,
            sync_service._handle_user_created
        )

    @pytest.mark.asyncio
    async def test_stop_service(self, mock_message_broker):
        # Create service instance
        sync_service = UserSyncService(mock_message_broker)
        
        # Mock connection
        mock_message_broker.connection = AsyncMock()
        
        # Stop service
        await sync_service.stop()
        
        # Verify connection was closed
        mock_message_broker.connection.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_user_created(self, db_session: Session, mock_message_broker):
        # Create service instance
        sync_service = UserSyncService(mock_message_broker)
        
        # Mock the get_db context manager
        mock_db_context = MagicMock()
        mock_db_context.__enter__ = MagicMock(return_value=db_session)
        mock_db_context.__exit__ = MagicMock(return_value=None)
        sync_service.get_db = MagicMock(return_value=mock_db_context)
        
        # Test user data
        user_data = {
            "email": "test@example.com",
            "firstname": "Test",
            "lastname": "User"
        }
        
        # Handle user created message
        await sync_service._handle_user_created(user_data)
        
        # Verify user was created
        user = db_session.query(User).filter(User.email == "test@example.com").first()
        assert user is not None
        assert user.email == "test@example.com"
        assert user.firstname == "Test"
        assert user.lastname == "User" 