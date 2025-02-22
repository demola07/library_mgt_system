from fastapi import APIRouter
from .routes import users, books, borrow, health

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(books.router, prefix="/books", tags=["books"])
api_router.include_router(borrow.router, prefix="/borrow", tags=["borrow"])
api_router.include_router(health.router, tags=["health"])
