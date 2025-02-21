import pytest
from app.services.user_service import UserService
from app.models.user import User
from app.schemas.user import UserCreate
from shared.message_types import MessageType

class TestUserService:
    @pytest.mark.asyncio
    async def test_create_user(self, db_session, mock_message_broker, sample_user_data):
        # Arrange
        user_service = UserService(mock_message_broker)
        user_create = UserCreate(**sample_user_data)

        # Act
        created_user = await user_service.create_user(db_session, user_create)

        # Assert
        assert created_user.email == sample_user_data["email"]
        assert created_user.firstname == sample_user_data["firstname"]
        mock_message_broker.publish.assert_called_once_with(
            MessageType.USER_CREATED.value,
            {
                "email": sample_user_data["email"],
                "firstname": sample_user_data["firstname"],
                "lastname": sample_user_data["lastname"]
            }
        )

    def test_get_user_by_email(self, db_session, mock_message_broker, sample_user_data):
        # Arrange
        user_service = UserService(mock_message_broker)
        db_user = User(**sample_user_data)
        db_session.add(db_user)
        db_session.commit()

        # Act
        result = user_service.get_user_by_email(db_session, sample_user_data["email"])

        # Assert
        assert result is not None
        assert result.email == sample_user_data["email"]

    def test_get_user(self, db_session, mock_message_broker, sample_user_data):
        # Arrange
        user_service = UserService(mock_message_broker)
        db_user = User(**sample_user_data)
        db_session.add(db_user)
        db_session.commit()

        # Act
        result = user_service.get_user(db_session, db_user.id)

        # Assert
        assert result is not None
        assert result.id == db_user.id
        assert result.email == sample_user_data["email"]

    @pytest.mark.asyncio
    async def test_create_existing_user(self, db_session, mock_message_broker, sample_user_data):
        # Arrange
        user_service = UserService(mock_message_broker)
        existing_user = User(**sample_user_data)
        db_session.add(existing_user)
        db_session.commit()

        user_create = UserCreate(**sample_user_data)

        # Act
        result = await user_service.create_user(db_session, user_create)

        # Assert
        assert result.id == existing_user.id
        assert result.email == existing_user.email
        mock_message_broker.publish.assert_not_called() 