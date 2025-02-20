from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from .core.config import settings
from .api import api_router
from .core.database import Base, engine
from .core.redis import start_subscriber

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
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
