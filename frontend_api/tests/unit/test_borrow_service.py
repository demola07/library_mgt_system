import pytest
from datetime import date, timedelta
from app.services.borrow_service import BorrowService
from app.models.book import Book
from app.models.user import User
from app.models.borrow import BorrowRecord
from app.schemas.borrow import BorrowCreate
from shared.message_types import MessageType

class TestBorrowService:
    @pytest.fixture
    def setup_book_and_user(self, db_session):
        # Create a test book
        book = Book(
            title="Test Book",
            author="Test Author",
            isbn="123-456-789",
            publisher="Test Publisher",
            category="Test Category",
            available=True
        )
        
        # Create a test user
        user = User(
            email="test@example.com",
            firstname="Test",
            lastname="User"
        )
        
        db_session.add(book)
        db_session.add(user)
        db_session.commit()
        
        return book, user

    @pytest.mark.asyncio
    async def test_create_borrow_record_success(
        self, 
        db_session, 
        mock_message_broker, 
        setup_book_and_user
    ):
        book, user = setup_book_and_user
        borrow_service = BorrowService(mock_message_broker)
        return_date = date.today() + timedelta(days=14)
        
        borrow_create = BorrowCreate(
            user_id=user.id,
            book_id=book.id,
            days=14
        )

        result = await borrow_service.create_borrow_record(db_session, borrow_create)

        assert result is not None
        assert result.user_id == user.id
        assert result.book_id == book.id
        assert result.return_date == return_date
        
        updated_book = db_session.query(Book).filter(Book.id == book.id).first()
        assert not updated_book.available
        
        mock_message_broker.publish.assert_called_once_with(
            MessageType.BOOK_BORROWED.value,
            {
                "book_isbn": book.isbn,
                "user_email": user.email,
                "return_date": return_date.isoformat()
            }
        )

    @pytest.mark.asyncio
    async def test_create_borrow_record_book_not_available(
        self, 
        db_session, 
        mock_message_broker, 
        setup_book_and_user
    ):
        book, user = setup_book_and_user
        book.available = False
        db_session.commit()
        
        borrow_service = BorrowService(mock_message_broker)
        borrow_create = BorrowCreate(
            user_id=user.id,
            book_id=book.id,
            days=14
        )

        with pytest.raises(ValueError) as exc_info:
            await borrow_service.create_borrow_record(db_session, borrow_create)
        
        assert "not available" in str(exc_info.value)
        mock_message_broker.publish.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_borrow_record_invalid_book(
        self, 
        db_session, 
        mock_message_broker, 
        setup_book_and_user
    ):
        _, user = setup_book_and_user
        borrow_service = BorrowService(mock_message_broker)
        borrow_create = BorrowCreate(
            user_id=user.id,
            book_id=999,  # Non-existent book ID
            days=14
        )

        with pytest.raises(ValueError) as exc_info:
            await borrow_service.create_borrow_record(db_session, borrow_create)
        
        assert "not found" in str(exc_info.value)
        mock_message_broker.publish.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_borrow_record_db_error(
        self, 
        db_session, 
        mock_message_broker, 
        setup_book_and_user
    ):
        book, user = setup_book_and_user
        borrow_service = BorrowService(mock_message_broker)
        borrow_create = BorrowCreate(
            user_id=user.id,
            book_id=book.id,
            days=14
        )
        
        # Mock db_session.commit to raise an exception
        def mock_commit():
            raise Exception("Database error")
        
        db_session.commit = mock_commit

        with pytest.raises(ValueError) as exc_info:
            await borrow_service.create_borrow_record(db_session, borrow_create)
        
        assert "Failed to create borrow record" in str(exc_info.value)
        mock_message_broker.publish.assert_not_called() 