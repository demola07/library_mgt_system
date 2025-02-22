import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.book import Book
from app.models.borrow import BorrowRecord
from datetime import datetime, timedelta
import uuid
from tests.integration.conftest import generate_unique_isbn

class TestUserEndpoints:
    @pytest.fixture
    def test_user(self, db_session: Session) -> User:
        user = User(
            email=f"test_{uuid.uuid4()}@example.com",  # Use unique email
            firstname="Test",
            lastname="User"
        )
        db_session.add(user)
        db_session.commit()
        return user

    @pytest.mark.asyncio
    async def test_list_users(self, client: AsyncClient, test_user: User):
        response = await client.get("/api/v1/users/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1  # At least our test user should be there

    @pytest.mark.asyncio
    async def test_list_users_with_borrowed_books(self, client: AsyncClient, db_session: Session, test_user: User):
        # Create a book and borrow record
        book = Book(
            title="Test Book",
            author="Test Author",
            isbn=f"ISBN-{str(uuid.uuid4())[:8]}",  # Generate unique ISBN
            publisher="Test Publisher",
            category="Test Category",
            available=False
        )
        db_session.add(book)
        db_session.commit()

        # Create borrow record
        borrow_record = BorrowRecord(
            book_id=book.id,
            user_id=test_user.id,
            borrow_date=datetime.now(),
            return_date=datetime.now() + timedelta(days=14)
        )
        db_session.add(borrow_record)
        db_session.commit()

        response = await client.get("/api/v1/users/borrowed-books")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1  # At least our test user should be there
        assert len(data["items"][0]["borrowed_books"]) >= 1  # User should have at least one borrowed book 