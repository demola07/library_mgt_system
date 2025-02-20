import json
import redis
from .config import settings

# Initialize Redis connection
redis_client = redis.from_url(settings.REDIS_URL)

def publish_book_updates(book_data_list: list[dict], action: str):
    """
    Publish multiple book updates to Redis for frontend service consumption.
    Uses Redis pipeline for bulk publishing.
    
    Args:
        book_data_list: List of book data to publish
        action: 'create' or 'delete'
    """
    # Create a pipeline to send all messages in one network round trip
    with redis_client.pipeline() as pipe:
        for book_data in book_data_list:
            message = {
                'action': action,
                'book': book_data
            }
            pipe.publish('book_updates', json.dumps(message))
        # Execute all publish commands in a single network round trip
        pipe.execute()


def publish_book_update(book_data: dict, action: str):
    """
    Publish a single book update to Redis for frontend service consumption.
    
    Args:
        book_data: Book data to publish
        action: 'create' or 'delete'
    """
    publish_book_updates([book_data], action)
