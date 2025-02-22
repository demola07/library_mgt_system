from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from sqlalchemy.exc import SQLAlchemyError
import logging
from .core.config import settings
from .api import api_router
from .core.database import Base, engine
from shared.message_broker import MessageBroker
from .services.book_service import BookService
from .services.user_service import UserService
from .services.user_sync_service import UserSyncService
from .services.borrow_sync_service import BorrowSyncService
from shared.exceptions import LibraryException
import traceback
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize shared message broker
message_broker = MessageBroker(settings.RABBITMQ_URL)

# Initialize services with shared message broker
book_service = BookService(message_broker)
user_service = UserService(message_broker)
user_sync_service = UserSyncService(message_broker)  # Pass the shared message broker
borrow_sync_service = BorrowSyncService(message_broker)  # Pass to this service too

app = FastAPI(
    title="Library Management System - Admin API",
    description="""Administrative API for the Library Management System.
    
    ## Features
    * 📚 Book catalogue management
    * 👤 User oversight
    * 📖 Borrowed books tracking
    
    ## Authentication
    Currently, the API does not require authentication for simplicity.
    Future versions will implement admin authentication.
    
    ## Notes
    - All timestamps are in UTC
    - Book updates are broadcasted via RabittMQ
    - Database changes are atomic and consistent
    - Supports bulk operations for efficiency
    """,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Library Admin Support",
        "url": "http://example.com/admin/support",
        "email": "admin-support@example.com",
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
    
    # Start the user sync service to listen for frontend user creation events
    logger.info("Starting user sync service...")
    await user_sync_service.start()

    # Start the borrow sync service to listen for frontend book borrowing events
    logger.info("Starting borrow sync service...")
    await borrow_sync_service.start()
    
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup connections on application shutdown"""
    logger.info("Shutting down application...")
    
    # Close message broker connection
    await message_broker.close()
    # Stop the user sync service
    await user_sync_service.stop()
    # Stop the borrow sync service
    await borrow_sync_service.stop()
    
    logger.info("Shutdown complete")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Global exception handlers (at the bottom)
@app.exception_handler(LibraryException)
async def library_exception_handler(request: Request, exc: LibraryException):
    """Handle custom library exceptions"""
    logger.error(
        f"Library error occurred: {exc.message}",
        extra={
            "error_code": exc.error_code,
            "details": exc.details,
            "path": request.url.path
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "type": "library_error"
        }
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database-related errors"""
    error_details = {
        "sql_state": getattr(exc, 'sqlstate', None),
        "path": request.url.path
    }
    logger.error(
        f"Database error occurred: {str(exc)}",
        extra=error_details,
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "DATABASE_ERROR",
            "message": "A database error occurred. Please try again later.",
            "type": "database_error"
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "type": "http_error"
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(
        f"Unhandled exception occurred: {str(exc)}",
        extra={
            "path": request.url.path,
            "traceback": traceback.format_exc()
        },
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred. Please try again later.",
            "type": "internal_error"
        }
    )
