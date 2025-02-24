import pytest
from unittest.mock import AsyncMock
from datetime import date
from sqlalchemy.orm import Session
from app.services.borrow_service import BorrowService
from app.models.book import Book
from app.models.user import User
from app.models.borrow import BorrowRecord
from shared.exceptions import ResourceNotFoundError, ValidationError

class TestBorrowService:
    @pytest.fixture
    def mock_message_broker(self):
        return AsyncMock()

    @pytest.fixture
    def test_book(self, db_session):
        book = Book(
            title="Test Book",
            author="Test Author",
            isbn="123-456-789",
            publisher="Test Publisher",
            category="Test Category",
            available=True
        )
        db_session.add(book)
        db_session.commit()
        return book

    @pytest.fixture
    def test_user(self, db_session):
        user = User(
            email="test@example.com",
            firstname="Test",
            lastname="User"
        )
        db_session.add(user)
        db_session.commit()
        return user

    @pytest.mark.asyncio
    async def test_create_borrow_record(self, db_session: Session, mock_message_broker, test_book, test_user):
        # Create service instance
        borrow_service = BorrowService(mock_message_broker)
        
        # Create borrow request data
        borrow_data = {
            "user_email": test_user.email,
            "book_isbn": test_book.isbn,
            "return_date": date.today()
        }
        
        # Create borrow record
        borrow_record = await borrow_service.create_borrow_record(db_session, borrow_data)
        
        # Verify borrow record was created
        assert borrow_record is not None
        assert borrow_record.user_id == test_user.id
        assert borrow_record.book_id == test_book.id
        
        # Verify book is no longer available
        db_session.refresh(test_book)
        assert test_book.available == False
        assert test_book.current_borrower_id == test_user.id

    @pytest.mark.asyncio
    async def test_create_borrow_record_unavailable_book(self, db_session: Session, mock_message_broker, test_book, test_user):
        # Create service instance
        borrow_service = BorrowService(mock_message_broker)
        
        # Make book unavailable
        test_book.available = False
        db_session.commit()
        
        # Create borrow request data
        borrow_data = {
            "user_email": test_user.email,
            "book_isbn": test_book.isbn,
            "return_date": date.today()
        }
        
        # Verify borrow attempt raises ValidationError
        with pytest.raises(ValidationError, match="Book is not available"):
            await borrow_service.create_borrow_record(db_session, borrow_data)

    @pytest.mark.asyncio
    async def test_create_borrow_record_nonexistent_book(self, db_session: Session, mock_message_broker, test_user):
        # Create service instance
        borrow_service = BorrowService(mock_message_broker)
        
        # Create borrow request data with non-existent ISBN
        borrow_data = {
            "user_email": test_user.email,
            "book_isbn": "999-999-999",
            "return_date": date.today()
        }
        
        # Verify borrow attempt raises ResourceNotFoundError
        with pytest.raises(ResourceNotFoundError, match="Book with identifier 999-999-999 not found"):
            await borrow_service.create_borrow_record(db_session, borrow_data)

    @pytest.mark.asyncio
    async def test_create_borrow_record_nonexistent_user(self, db_session: Session, mock_message_broker, test_book):
        # Create service instance
        borrow_service = BorrowService(mock_message_broker)
        
        # Create borrow request data with non-existent user
        borrow_data = {
            "user_email": "nonexistent@example.com",
            "book_isbn": test_book.isbn,
            "return_date": date.today()
        }
        
        # Verify borrow attempt raises ResourceNotFoundError
        with pytest.raises(ResourceNotFoundError, match="User with identifier nonexistent@example.com not found"):
            await borrow_service.create_borrow_record(db_session, borrow_data) 