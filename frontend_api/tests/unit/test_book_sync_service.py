import pytest
from app.services.book_sync_service import BookSyncService
from app.models.book import Book
from app.services.book_service import BookService
from shared.message_types import MessageType
from sqlalchemy.orm import Session
from unittest.mock import patch, AsyncMock

class TestBookSyncService:
    @pytest.mark.asyncio
    async def test_start_service(self, mock_message_broker):
        # Arrange
        sync_service = BookSyncService()
        sync_service.message_broker = mock_message_broker

        # Act
        await sync_service.start()

        # Assert
        mock_message_broker.connect.assert_called_once()
        assert mock_message_broker.subscribe.call_count == 2
        mock_message_broker.subscribe.assert_any_call(
            MessageType.BOOKS_CREATED.value,
            sync_service._handle_books_created
        )
        mock_message_broker.subscribe.assert_any_call(
            MessageType.BOOK_DELETED.value,
            sync_service._handle_book_deleted
        )

    @pytest.mark.asyncio
    async def test_stop_service(self, mock_message_broker):
        # Arrange
        sync_service = BookSyncService()
        sync_service.message_broker = mock_message_broker
        mock_message_broker.connection = mock_message_broker  # Mock connection property

        # Act
        await sync_service.stop()

        # Assert
        mock_message_broker.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_books_created(self, db_session: Session, mock_message_broker):
        # Create BookService instance with mock message broker
        book_service = BookService(mock_message_broker)
        
        # Create BookSyncService with the book_service
        sync_service = BookSyncService()
        sync_service.book_service = book_service  # Inject the book service
        
        # Mock the book_service.create_books method
        async def mock_create_books(db, books_data, *args, **kwargs):
            book_data = books_data[0]  # Get the first book data
            book = Book(
                title=book_data.title,
                author=book_data.author,
                isbn=book_data.isbn,
                publisher=book_data.publisher,
                category=book_data.category,
                available=True  # Set default since it might not be in the model
            )
            db_session.add(book)
            db_session.commit()
            return [book]
            
        book_service.create_books = AsyncMock(side_effect=mock_create_books)
        
        books_data = [{
            "title": "New Book",
            "author": "New Author",
            "isbn": "123-456-789",
            "publisher": "Test Publisher",
            "category": "Test Category",
            "available": True
        }]

        # Call the handler
        await sync_service._handle_books_created(books_data)
        
        # Explicitly query for the book
        created_book = db_session.query(Book).filter(Book.isbn == "123-456-789").first()
        
        # Print debug information
        print(f"Created book: {created_book}")
        if created_book is None:
            existing_books = db_session.query(Book).all()
            print(f"All books in DB: {existing_books}")
        
        assert created_book is not None
        assert created_book.title == "New Book"
        assert created_book.available == True

    @pytest.mark.asyncio
    async def test_handle_book_deleted(self, db_session: Session, mock_message_broker):
        # Create BookService instance with mock message broker
        book_service = BookService(mock_message_broker)
        
        # Create BookSyncService with the book_service
        sync_service = BookSyncService()
        sync_service.book_service = book_service  # Inject the book service
        
        # Create a book first
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
        
        # Verify book exists
        existing_book = db_session.query(Book).filter(Book.isbn == "123-456-789").first()
        assert existing_book is not None, "Book was not created properly"
        
        # Mock the book_service.delete_book_by_isbn method
        async def mock_delete_book(*args, **kwargs):
            isbn = args[1]  # Get the ISBN from args
            book = db_session.query(Book).filter(Book.isbn == isbn).first()
            if book:
                db_session.delete(book)
                db_session.commit()
                return True
            return False
            
        book_service.delete_book_by_isbn = AsyncMock(side_effect=mock_delete_book)
        
        delete_data = {"isbn": "123-456-789"}
        
        # Call the handler
        await sync_service._handle_book_deleted(delete_data)
        
        # Refresh the session and check if book was deleted
        db_session.expire_all()
        deleted_book = db_session.query(Book).filter(Book.isbn == "123-456-789").first()
        
        # Print debug information
        if deleted_book is not None:
            print(f"Book still exists: {deleted_book.__dict__}")
            
        assert deleted_book is None, "Book was not deleted" 