# frontend_api/tests/unit/test_book_service.py
import pytest
from datetime import datetime
from app.services.book_service import BookService
from app.models.book import Book
from app.schemas.book import BookCreate, BookList
from shared.message_types import MessageType

class TestBookService:
    @pytest.mark.asyncio
    async def test_get_book(self, db_session, sample_book_data, mock_message_broker):
        # Arrange
        book_service = BookService(mock_message_broker)
        db_book = Book(**sample_book_data)
        db_session.add(db_book)
        db_session.commit()

        # Act
        result = book_service.get_book(db_session, db_book.id)

        # Assert
        assert result is not None
        assert result.title == sample_book_data["title"]
        assert result.isbn == sample_book_data["isbn"]

    @pytest.mark.asyncio
    async def test_get_books_with_filters(self, db_session, mock_message_broker):
        # Arrange
        book_service = BookService(mock_message_broker)
        books_data = [
            {
                "title": "Book 1",
                "author": "Author 1",
                "isbn": "123",
                "publisher": "Publisher A",
                "category": "Fiction",
                "available": True
            },
            {
                "title": "Book 2",
                "author": "Author 2",
                "isbn": "456",
                "publisher": "Publisher B",
                "category": "Science",
                "available": True
            }
        ]
        
        for book_data in books_data:
            db_book = Book(**book_data)
            db_session.add(db_book)
        db_session.commit()

        # Act
        result = book_service.get_books(
            db_session,
            page=1,
            limit=10,
            publisher="Publisher A",
            category="Fiction"
        )

        # Assert
        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0].title == "Book 1"

    @pytest.mark.asyncio
    async def test_create_books(self, db_session, mock_message_broker, sample_book_data):
        # Arrange
        book_service = BookService(mock_message_broker)
        book_data = BookCreate(**sample_book_data)

        # Act
        created_books = await book_service.create_books(db_session, [book_data])

        # Assert
        assert len(created_books) == 1
        assert created_books[0].title == sample_book_data["title"]
        mock_message_broker.publish.assert_not_called()