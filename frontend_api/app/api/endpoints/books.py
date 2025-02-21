from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from ...core.database import get_db
from ...schemas.book import BookResponse, BookList, BookCreate, BookDetail
from ...services.book_service import BookService
from shared.message_broker import MessageBroker
from shared.pagination import PaginatedResponse

router = APIRouter()

# Dependency to get BookService instance
def get_book_service():
    rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
    return BookService(MessageBroker(rabbitmq_url=rabbitmq_url))

@router.get("/", response_model=PaginatedResponse[BookList])
def list_available_books(
    page: int = 1,
    limit: int = 10,
    publisher: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    book_service: BookService = Depends(get_book_service)
):
    """List available books with optional filtering and pagination."""
    return book_service.get_books(db, page=page, limit=limit, publisher=publisher, category=category)

@router.get("/{book_id}", response_model=BookDetail)
def get_book(
    book_id: int = Path(..., description="Book ID"),
    db: Session = Depends(get_db),
    book_service: BookService = Depends(get_book_service)
):
    """Get detailed information about a specific book."""
    book = book_service.get_book(db, book_id=book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return BookDetail.model_validate(book)

@router.get("/publishers/{publisher}/", response_model=PaginatedResponse[BookResponse])
async def filter_books_by_publisher(
    publisher: str, 
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    book_service: BookService = Depends(get_book_service)
):
    """Get books filtered by publisher with pagination."""
    return await book_service.get_books_by_publisher(db, publisher, page=page, limit=limit)

@router.get("/categories/{category}/", response_model=PaginatedResponse[BookResponse])
async def filter_books_by_category(
    category: str, 
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    book_service: BookService = Depends(get_book_service)
):
    """Get books filtered by category with pagination."""
    return await book_service.get_books_by_category(db, category, page=page, limit=limit)
