import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from app.models.book import Book
from datetime import datetime, timedelta
import uuid
from unittest.mock import AsyncMock, patch

class TestBookEndpoints:
    @pytest.fixture
    def test_book(self, db_session: Session) -> Book:
        book = Book(
            title="Test Book",
            author="Test Author",
            isbn=f"ISBN-{str(uuid.uuid4())[:8]}",
            publisher="Test Publisher",
            category="Test Category",
            available=True
        )
        db_session.add(book)
        db_session.commit()
        return book

    @pytest.mark.asyncio
    async def test_create_books(self, client: AsyncClient):
        books_data = [
            {
                "title": "New Book 1",
                "author": "Author 1",
                "isbn": f"ISBN-{str(uuid.uuid4())[:8]}",
                "publisher": "Publisher 1",
                "category": "Category 1"
            },
            {
                "title": "New Book 2",
                "author": "Author 2",
                "isbn": f"ISBN-{str(uuid.uuid4())[:8]}",
                "publisher": "Publisher 2",
                "category": "Category 2"
            }
        ]

        response = await client.post("/api/v1/books/bulk", json=books_data)
        assert response.status_code == 200

    @pytest.mark.asyncio
    @patch('app.services.book_service.book_service.message_broker')
    async def test_delete_book(self, mock_broker, client: AsyncClient, test_book: Book, db_session: Session):
        # Mock the message broker publish method
        mock_broker.publish = AsyncMock()
        
        response = await client.delete(f"/api/v1/books/{test_book.id}")
        assert response.status_code == 200
        
        # Verify the message was published
        mock_broker.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_unavailable_books(self, client: AsyncClient, db_session: Session):
        # Create a new unavailable book specifically for this test
        book = Book(
            title="Unavailable Test Book",
            author="Test Author",
            isbn=f"ISBN-{str(uuid.uuid4())[:8]}",
            publisher="Test Publisher",
            category="Test Category",
            available=False  # Set as unavailable from the start
        )
        db_session.add(book)
        db_session.commit()

        # Verify the book exists and is unavailable
        db_book = db_session.query(Book).filter(Book.id == book.id).first()
        assert db_book is not None
        assert db_book.available is False

        # Print all books in the database for debugging
        all_books = db_session.query(Book).all()
        print("\nAll books in database:")
        for b in all_books:
            print(f"Book ID: {b.id}, Title: {b.title}, Available: {b.available}")

        # Print specifically unavailable books
        unavailable_books = db_session.query(Book).filter(Book.available == False).all()
        print("\nUnavailable books in database:")
        for b in unavailable_books:
            print(f"Book ID: {b.id}, Title: {b.title}, Available: {b.available}")

        response = await client.get("/api/v1/books/unavailable")
        assert response.status_code == 200
        data = response.json()

        print(f"\nResponse data: {data}")
        print(f"Test book details - ID: {book.id}, Title: {book.title}, Available: {book.available}")

        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1  # At least our test book should be there
        
        # Verify the book is in the response items
        book_ids = [b["id"] for b in data["items"]]
        assert book.id in book_ids 