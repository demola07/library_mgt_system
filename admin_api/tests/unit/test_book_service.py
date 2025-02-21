import pytest
from unittest.mock import AsyncMock, patch
from app.services.book_service import BookService
from app.models.book import Book
from app.models.borrow import BorrowRecord
from app.schemas.book import BookCreate
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

class TestBookService:
    @pytest.fixture
    def mock_message_broker(self):
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_create_books(self, db_session: Session, mock_message_broker):
        # Create service instance
        book_service = BookService(mock_message_broker)
        
        # Test data
        books_data = [BookCreate(
            title="Test Book",
            author="Test Author",
            isbn="123-456-789",
            publisher="Test Publisher",
            category="Test Category"
        )]
        
        # Create books
        created_books = await book_service.create_books(db_session, books_data)
        
        # Verify books were created
        assert len(created_books) == 1
        assert created_books[0].title == "Test Book"
        assert created_books[0].isbn == "123-456-789"
        
        # Verify message was published
        mock_message_broker.publish.assert_called_once()
        
        # Verify book exists in database
        db_book = db_session.query(Book).filter(Book.isbn == "123-456-789").first()
        assert db_book is not None
        assert db_book.title == "Test Book"

    @pytest.mark.asyncio
    async def test_get_book(self, db_session: Session, mock_message_broker):
        # Create service instance
        book_service = BookService(mock_message_broker)
        
        # Create test book
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
        
        # Get book
        retrieved_book = book_service.get_book(db_session, book.id)
        
        # Verify book was retrieved
        assert retrieved_book is not None
        assert retrieved_book.title == "Test Book"
        assert retrieved_book.isbn == "123-456-789"

    @pytest.mark.asyncio
    async def test_delete_book(self, db_session: Session, mock_message_broker):
        # Create service instance
        book_service = BookService(mock_message_broker)
        
        # Create test book
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
        
        # Delete book
        success = await book_service.delete_book(db_session, book.id)
        
        # Verify deletion was successful
        assert success is True
        
        # Verify message was published
        mock_message_broker.publish.assert_called_once()
        
        # Verify book was deleted from database
        db_book = db_session.query(Book).filter(Book.id == book.id).first()
        assert db_book is None

    @pytest.mark.asyncio
    async def test_get_unavailable_books(self, db_session: Session, mock_message_broker):
        # Create service instance
        book_service = BookService(mock_message_broker)
        
        # Create test book and borrow record
        book = Book(
            title="Test Book",
            author="Test Author",
            isbn="123-456-789",
            publisher="Test Publisher",
            category="Test Category",
            available=False
        )
        db_session.add(book)
        db_session.flush()  # Get the book ID
        
        # Create borrow record
        borrow_record = BorrowRecord(
            book_id=book.id,
            user_id=1,  # Test user ID
            borrow_date=datetime.now(),
            return_date=datetime.now() + timedelta(days=14)
        )
        db_session.add(borrow_record)
        db_session.commit()
        
        # Get unavailable books
        paginated_response = await book_service.get_unavailable_books(db_session, page=1, limit=10)
        
        # Verify response
        assert paginated_response.total == 1
        assert len(paginated_response.items) == 1
        assert paginated_response.items[0].isbn == "123-456-789"