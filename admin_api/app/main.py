from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from .core.config import settings
from .api import api_router
from .core.database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Library Management System - Admin API",
    description="""Administrative API for the Library Management System.
    
    ## Features
    * 📚 Book catalogue management
    * 👤 User oversight
    * 📖 Book tracking system
    * 🔔 Real-time notifications
    * 📈 System monitoring
    
    ## Authentication
    Currently, the API does not require authentication for simplicity.
    Future versions will implement admin authentication.
    
    ## Notes
    - All timestamps are in UTC
    - Book updates are broadcasted via Redis
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

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=[
            {"name": "books", "description": "Book catalogue management operations."},
            {"name": "users", "description": "User management and oversight."},
            {"name": "health", "description": "API health check endpoints."},
        ],
    )
    
    # Add security schemes if needed in the future
    # openapi_schema["components"]["securitySchemes"] = {...}
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
