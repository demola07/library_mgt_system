import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import Base, engine, get_db
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
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

def generate_unique_isbn():
    """Generate a unique ISBN for test data"""
    return f"ISBN-{str(uuid.uuid4())[:8]}"

@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client 