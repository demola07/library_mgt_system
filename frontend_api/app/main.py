from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import asyncio
from .core.config import settings
from .api import api_router
from .core.database import Base, engine
from .core.redis import start_subscriber

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Library Management System - Frontend API",
    description="""Frontend API for the Library Management System.
    
    ## Features
    * 📚 Browse and search books
    * 👤 User enrollment and management
    * 📖 Book borrowing system
    * 🔍 Filter books by publisher and category
    * ⚡ Real-time book availability updates
    
    ## Authentication
    Currently, the API does not require authentication for simplicity.
    
    ## Notes
    - All timestamps are in UTC
    - Book availability is updated in real-time via Redis
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
    """Start the Redis subscriber when the application starts"""
    # Start Redis subscriber in the background
    asyncio.create_task(start_subscriber())

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=[
            {"name": "books", "description": "Operations with books, including listing and filtering."},
            {"name": "users", "description": "User management operations."},
            {"name": "borrow", "description": "Book borrowing operations."},
            {"name": "health", "description": "API health check endpoints."},
        ],
    )
    
    # Add security schemes if needed in the future
    # openapi_schema["components"]["securitySchemes"] = {...}
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
