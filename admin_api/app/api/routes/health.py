from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from ...core.database import get_db
from ...services.book_service import message_broker  # Import the shared message broker instance

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint that verifies database and RabbitMQ connections"""
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        
        # Check RabbitMQ connection
        await message_broker.connect()  # This will establish connection if not already connected
        if not message_broker.connection or message_broker.connection.is_closed:
            raise Exception("RabbitMQ connection is closed")
        
        return {
            "service": "admin_api",
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
