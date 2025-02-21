import pytest
from unittest.mock import AsyncMock
from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app.models.user import User
from app.models.borrow import BorrowRecord
from app.models.book import Book
from datetime import datetime

class TestUserService:
    @pytest.fixture
    def mock_message_broker(self):
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_get_users(self, db_session: Session, mock_message_broker):
        # Create service instance
        user_service = UserService(mock_message_broker)
        
        # Create test users
        users = [
            User(email=f"test{i}@example.com", firstname=f"Test{i}", lastname=f"User{i}", created_at=datetime.utcnow())
            for i in range(3)
        ]
        for user in users:
            db_session.add(user)
        db_session.commit()
        
        # Get paginated users
        result = await user_service.get_users(db_session, page=1, limit=2)
        
        # Verify pagination
        assert result.total == 3
        assert len(result.items) == 2
        assert result.page == 1
        assert result.limit == 2

    @pytest.mark.asyncio
    async def test_get_users_with_borrowed_books(self, db_session: Session, mock_message_broker):
        # Create service instance
        user_service = UserService(mock_message_broker)
        
        # Create test user
        user = User(email="test@example.com", firstname="Test", lastname="User", created_at=datetime.utcnow())
        db_session.add(user)
        db_session.flush()
        
        # Create test book
        book = Book(
            title="Test Book",
            author="Test Author",
            isbn="123-456-789",
            publisher="Test Publisher",
            category="Test Category"
        )
        db_session.add(book)
        db_session.flush()
        
        # Create borrow record
        borrow = BorrowRecord(
            user_id=user.id,
            book_id=book.id,
            borrow_date=datetime.utcnow(),
            return_date=datetime.utcnow()
        )
        db_session.add(borrow)
        db_session.commit()
        
        # Get users with borrowed books
        result = await user_service.get_users_with_borrowed_books(db_session, page=1, limit=10)
        
        # Verify result
        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0].email == "test@example.com"
        assert len(result.items[0].borrowed_books) == 1
        assert result.items[0].borrowed_books[0].isbn == "123-456-789"

    def test_get_user_by_email(self, db_session: Session, mock_message_broker):
        # Create service instance
        user_service = UserService(mock_message_broker)
        
        # Create test user
        user = User(
            email="test@example.com",
            firstname="Test",
            lastname="User",
            created_at=datetime.utcnow()
        )
        db_session.add(user)
        db_session.commit()
        
        # Get user by email
        retrieved_user = user_service.get_user_by_email(db_session, "test@example.com")
        
        # Verify user was retrieved
        assert retrieved_user is not None
        assert retrieved_user.email == "test@example.com"
        assert retrieved_user.firstname == "Test"

    @pytest.mark.asyncio
    async def test_create_user_from_frontend(self, db_session: Session, mock_message_broker):
        # Create service instance
        user_service = UserService(mock_message_broker)
        
        # Test user data
        user_data = {
            "email": "test@example.com",
            "firstname": "Test",
            "lastname": "User"
        }
        
        # Create user
        user = await user_service.create_user_from_frontend(db_session, user_data)
        
        # Verify user was created
        assert user is not None
        assert user.email == "test@example.com"
        assert user.firstname == "Test"
        assert user.lastname == "User"
        
        # Verify user exists in database
        db_user = db_session.query(User).filter(User.email == "test@example.com").first()
        assert db_user is not None

    @pytest.mark.asyncio
    async def test_create_user_from_frontend_duplicate(self, db_session: Session, mock_message_broker):
        # Create service instance
        user_service = UserService(mock_message_broker)
        
        # Create initial user
        user_data = {
            "email": "test@example.com",
            "firstname": "Test",
            "lastname": "User"
        }
        await user_service.create_user_from_frontend(db_session, user_data)
        
        # Try to create duplicate user
        duplicate_user = await user_service.create_user_from_frontend(db_session, user_data)
        
        # Should return existing user instead of creating new one
        assert duplicate_user is not None
        assert duplicate_user.email == "test@example.com"
        
        # Verify only one user exists in database
        user_count = db_session.query(User).filter(User.email == "test@example.com").count()
        assert user_count == 1 