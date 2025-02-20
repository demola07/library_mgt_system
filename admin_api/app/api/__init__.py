from fastapi import APIRouter
from .endpoints import books, users

api_router = APIRouter()

api_router.include_router(books.router, prefix="/books", tags=["books"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
