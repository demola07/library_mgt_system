import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import Base, engine, get_db
from app.models.user import User
from app.models.book import Book
from app.models.borrow import BorrowRecord
from typing import AsyncGenerator, Generator
import uuid
from fastapi.testclient import TestClient

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop all tables after all tests
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def db_session() -> Generator[Session, None, None]:
    # Create a new session for each test
    session = Session(bind=engine)
    try:
        yield session
    finally:
        session.rollback()  # Roll back any pending transactions
        session.close()

@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

def generate_unique_isbn():
    """Generate a unique ISBN for test data"""
    return f"ISBN-{str(uuid.uuid4())[:8]}"

@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def test_user(db_session):
    """Create test user"""
    # Use a unique email for each test
    unique_id = str(uuid.uuid4())[:8]
    user = User(
        email=f"test{unique_id}@example.com",
        firstname="Test",
        lastname="User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    yield user
    db_session.delete(user)
    db_session.commit()

@pytest.fixture
def test_book(db_session):
    """Create test book"""
    book = Book(
        title="Test Book",
        author="Test Author",
        isbn=generate_unique_isbn(),
        publisher="Test Publisher",
        category="Fiction",
        available=True
    )
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)
    yield book
    db_session.delete(book)
    db_session.commit()

@pytest.fixture
def borrowed_test_book(db_session, test_book, test_user):
    """Create a borrowed test book"""
    test_book.available = False
    borrow = BorrowRecord(
        user_id=test_user.id,
        book_id=test_book.id
        # Removed the 'days' parameter since it's not in the model
    )
    db_session.add(borrow)
    db_session.commit()
    db_session.refresh(test_book)
    yield test_book
    db_session.delete(borrow)
    test_book.available = True
    db_session.commit() 