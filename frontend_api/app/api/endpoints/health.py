from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from redis.asyncio import Redis

from ...core.database import get_db
from ...core.redis import redis_client

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint that verifies database and Redis connections"""
    try:
        # Check database connection
        db.execute("SELECT 1")
        
        # Check Redis connection
        await redis_client.ping()
        
        return {
            "status": "healthy",
            "database": "connected",
            "redis": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
