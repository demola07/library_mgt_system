import asyncio
import httpx
import json
from datetime import date, timedelta
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API endpoints - using Docker service names
FRONTEND_API = "http://bookstore-frontend_api-1:8000/api/v1"
ADMIN_API = "http://bookstore-admin_api-1:8000/api/v1"  # Note: using port 8000, not 8001

# Sample data
BOOKS = [
    {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "isbn": "978-0132350884",
        "publisher": "Manning Publications",
        "category": "Software Development",
        "available": True
    },
    {
        "title": "Design Patterns",
        "author": "Erich Gamma",
        "isbn": "978-0201633610",
        "publisher": "Wiley",
        "category": "Software Architecture",
        "available": True
    },
    {
        "title": "The Lean Startup",
        "author": "Eric Ries",
        "isbn": "978-0307887894",
        "publisher": "O'Reilly Media",
        "category": "Business & Entrepreneurship"
    },
    {
        "title": "Steve Jobs",
        "author": "Walter Isaacson",
        "isbn": "978-1451648539",
        "publisher": "Simon & Schuster",
        "category": "Biography"
    },
    {
        "title": "A Brief History of Time",
        "author": "Stephen Hawking",
        "isbn": "978-0553380163",
        "publisher": "Bantam Books",
        "category": "Popular Science"
    },
    {
        "title": "1984",
        "author": "George Orwell",
        "isbn": "978-0451524935",
        "publisher": "Penguin Books",
        "category": "Classic Fiction"
    },
    {
        "title": "The World War II",
        "author": "Winston Churchill",
        "isbn": "978-0395416853",
        "publisher": "Houghton Mifflin",
        "category": "Military History"
    }
]

USERS = [
    {
        "email": "john.doe2@example.com",
        "firstname": "John",
        "lastname": "Doe"
    },
    {
        "email": "jane.smith2@example.com",
        "firstname": "Jane",
        "lastname": "Smith"
    },
    {
        "email": "bob.wilson2@example.com",
        "firstname": "Bob",
        "lastname": "Wilson"
    }
]

async def create_user(client: httpx.AsyncClient, user_data: dict) -> dict:
    """Create user through frontend API which will broadcast to admin"""
    try:
        # Log the request data for debugging
        logger.info(f"Creating user with data: {user_data}")
        response = await client.post(f"{FRONTEND_API}/users/", json=user_data)
        response.raise_for_status()
        logger.info(f"Created user: {user_data['email']}")
        return response.json()
    except Exception as e:
        logger.error(f"Failed to create user {user_data['email']}: {str(e)}")
        # Log the response content if available
        if hasattr(e, 'response'):
            logger.error(f"Response content: {e.response.content}")
        raise

async def create_books_bulk(client: httpx.AsyncClient, books: list) -> list:
    """Create books in bulk through admin API"""
    try:
        response = await client.post(f"{ADMIN_API}/books/bulk", json=books)
        response.raise_for_status()
        logger.info(f"Created {len(books)} books in bulk")
        return response.json()
    except Exception as e:
        logger.error(f"Failed to create books in bulk: {str(e)}")
        if hasattr(e, 'response'):
            logger.error(f"Response content: {e.response.content}")
        raise

async def create_mock_data():
    """Create mock data using actual API endpoints"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Create users one at a time through frontend API
            logger.info("Creating users...")
            created_users = []
            for user_data in USERS:
                try:
                    user = await create_user(client, user_data)
                    created_users.append(user)
                    logger.info(f"Created user: {user_data['email']}")
                    await asyncio.sleep(3)  # Wait for sync
                except Exception as e:
                    logger.error(f"Failed to create user {user_data['email']}, continuing with next user")
                    if hasattr(e, 'response'):
                        logger.error(f"Response content: {e.response.content}")
                    continue

            # Create books in bulk through admin API
            logger.info("Creating books...")
            try:
                created_books = await create_books_bulk(client, BOOKS)
                for book in created_books:
                    logger.info(f"Created book: {book['title']}")
                await asyncio.sleep(2)  # Wait for sync
            except Exception as e:
                logger.error("Failed to create books")
                if hasattr(e, 'response'):
                    logger.error(f"Response content: {e.response.content}")

            logger.info("Mock data creation completed!")

        except Exception as e:
            logger.error(f"Error in mock data creation process: {str(e)}")
            raise

async def verify_services():
    """Verify that both services are running before starting"""
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            # Check frontend API
            frontend_health = await client.get(f"{FRONTEND_API}/health")
            logger.info("Frontend API is running")
        except Exception as e:
            logger.error(f"Frontend API is not accessible: {str(e)}")
            raise

        try:
            # Check admin API
            admin_health = await client.get(f"{ADMIN_API}/health")
            logger.info("Admin API is running")
        except Exception as e:
            logger.error(f"Admin API is not accessible: {str(e)}")
            raise

if __name__ == "__main__":
    try:
        # First verify services are running
        asyncio.run(verify_services())
        
        # Then run the mock data creation
        asyncio.run(create_mock_data())
        
        # Wait a bit for messages to be processed
        asyncio.run(asyncio.sleep(5))
        
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        raise
