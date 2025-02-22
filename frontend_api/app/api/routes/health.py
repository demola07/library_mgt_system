from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from ...core.database import get_db
from ...services.book_sync_service import book_sync_service

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint that verifies database and RabbitMQ connections"""
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        
        # Check RabbitMQ connection using the shared message broker
        await book_sync_service.message_broker.connect()
        if not book_sync_service.message_broker.connection:
            raise Exception("RabbitMQ connection is closed")
        
        return {
            "status": "healthy",
            "database": "connected",
            "rabbitmq": "connected"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "error": str(e)
            }
        )
