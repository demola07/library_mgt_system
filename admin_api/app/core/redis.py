import json
import redis
from .config import settings

# Initialize Redis connection
redis_client = redis.from_url(settings.REDIS_URL)

def publish_book_update(book_data: dict, action: str):
    """
    Publish book updates to Redis for frontend service consumption
    action: 'create' or 'delete'
    """
    message = {
        'action': action,
        'book': book_data
    }
    redis_client.publish('book_updates', json.dumps(message))
