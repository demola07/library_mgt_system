from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import asyncio
from .core.config import settings
from .api import api_router
from .core.database import Base, engine
from shared.message_broker import MessageBroker
from .services.book_sync_service import BookSyncService
from .services.book_service import BookService
from .services.user_service import UserService
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize shared message broker
message_broker = MessageBroker(settings.RABBITMQ_URL)

# Initialize services with shared message broker
book_sync_service = BookSyncService()
book_service = BookService(message_broker)
user_service = UserService(message_broker)

app = FastAPI(
    title="Library Management System - Frontend API",
    description="""Frontend API for the Library Management System.
    
    ## Features
    * 📚 Browse and search books
    * 👤 User enrollment and management
    * 📖 Book borrowing system
    * 🔍 Filter books by publisher and category
    * ⚡ Real-time book borrowing updates
    
    ## Authentication
    Currently, the API does not require authentication for simplicity.
    
    ## Notes
    - All timestamps are in UTC
    - Book borrowing is updated in real-time via RabbitMQ
    - Database changes are atomic and consistent
    """,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Library Support",
        "url": "http://example.com/support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """Initialize services and connections on application startup"""
    logger.info("Connecting to RabbitMQ...")
    await message_broker.connect()
    
    # Start the book sync service
    logger.info("Starting book sync service...")
    await book_sync_service.start()
    
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup connections on application shutdown"""
    logger.info("Shutting down application...")
    
    # Close message broker connection
    await message_broker.close()
    
    # Stop the book sync service
    await book_sync_service.stop()
    
    logger.info("Shutdown complete")

# Global exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error occurred. Please try again later.",
            "type": "internal_error"
        }
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database-related errors."""
    logger.error(f"Database error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Database error occurred. Please try again later.",
            "type": "database_error"
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with custom format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "type": "http_error"
        }
    )

