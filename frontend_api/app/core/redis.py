import json
import asyncio
import redis.asyncio as redis
from sqlalchemy.orm import Session
from ..services import book_service
from ..core.database import SessionLocal
from ..schemas.book import BookCreate
from .config import settings

# Initialize Redis connection
redis_client = redis.from_url(settings.REDIS_URL)

async def process_book_update(message: dict, db: Session):
    """Process book updates received from Admin API"""
    action = message.get('action')
    book_data = message.get('book')
    
    if not action or not book_data:
        return
        
    if action == 'create':
        # Create book from received data
        book_create = BookCreate(**book_data)
        book_service.create_book(db, book_create)
    elif action == 'delete':
        # Delete book if it exists
        book_id = book_data.get('id')
        if book_id:
            book_service.delete_book(db, book_id)

async def start_subscriber():
    """Start the Redis subscriber for book updates"""
    try:
        pubsub = redis_client.pubsub()
        await pubsub.subscribe('book_updates')
        
        while True:
            try:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message and message['type'] == 'message':
                    # Parse message data
                    data = json.loads(message['data'])
                    
                    # Create a new database session
                    db = SessionLocal()
                    try:
                        await process_book_update(data, db)
                    finally:
                        db.close()
                        
                # Small sleep to prevent CPU overuse
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"Error processing message: {e}")
                await asyncio.sleep(1)  # Wait before retrying
                
    except Exception as e:
        print(f"Redis subscription error: {e}")
        # Attempt to reconnect after a delay
        await asyncio.sleep(5)
        await start_subscriber()
