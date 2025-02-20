from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database import get_db
from ...schemas.book import Book, BookList
from ...models.book import Category, Publisher
from ...services import book_service

router = APIRouter()

@router.get("/", response_model=List[BookList], summary="List available books")
def list_available_books(
    skip: int = 0,
    limit: int = 100,
    publisher: Optional[Publisher] = None,
    category: Optional[Category] = None,
    db: Session = Depends(get_db)
):
    """List available books with optional filtering and pagination."""
    return book_service.get_books(
        db,
        skip=skip,
        limit=limit,
        publisher=publisher,
        category=category,
        available_only=True  # Always show only available books
    )

@router.get("/{book_id}", response_model=Book, summary="Get a specific book")
def get_book(
    book_id: int = Path(..., description="Book ID"),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific book."""
    book = book_service.get_book(db, book_id=book_id)
    
    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )
    
    return book

@router.get("/publishers/", response_model=List[str], summary="List all publishers")
def get_publishers():
    """Get a list of all publishers."""
    return [publisher.value for publisher in Publisher]

@router.get("/categories/", response_model=List[str], summary="List all categories")
def get_categories():
    """Get a list of all book categories."""
    return [category.value for category in Category]
