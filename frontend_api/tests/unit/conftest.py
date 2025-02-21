# frontend_api/tests/conftest.py
import pytest
from unittest.mock import Mock, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# Use absolute imports instead of relative imports
from app.core.database import Base, get_db
from app.main import app
from shared.message_broker import MessageBroker

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_session() -> Session:
    # Create an in-memory SQLite database for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    
    # Create all tables
    from app.models.book import Base
    Base.metadata.create_all(engine)
    
    # Create a new session
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    
    # Create a new session for each test
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture
def mock_message_broker():
    mock = AsyncMock(spec=MessageBroker)
    mock.publish = AsyncMock()
    mock.subscribe = AsyncMock()
    mock.connect = AsyncMock()
    mock.close = AsyncMock()
    mock.connection = Mock()
    return mock

@pytest.fixture
def sample_book_data():
    return {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "isbn": "978-0132350884",
        "publisher": "Manning Publications",
        "category": "Software Development",
        "available": True
    }

@pytest.fixture
def sample_user_data():
    return {
        "email": "test@example.com",
        "firstname": "Test",
        "lastname": "User"
    }