from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database import get_db
from ...schemas.book import Book, BookList
from ...models.book import Category, Publisher
from ...services import book_service

router = APIRouter()

@router.get("/", response_model=List[BookList])
def list_books(
    skip: int = 0,
    limit: int = 100,
    publisher: Optional[Publisher] = None,
    category: Optional[Category] = None,
    available_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    List all books with optional filtering by publisher and category.
    Only shows available books if available_only is True.
    """
    return book_service.get_books(
        db,
        skip=skip,
        limit=limit,
        publisher=publisher,
        category=category,
        available_only=available_only
    )

@router.get("/{book_id}", response_model=Book)
def get_book(book_id: int, db: Session = Depends(get_db)):
    """Get a specific book by ID"""
    db_book = book_service.get_book(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@router.get("/publishers/", response_model=List[str])
def get_publishers():
    """Get list of all publishers"""
    return [publisher.value for publisher in Publisher]

@router.get("/categories/", response_model=List[str])
def get_categories():
    """Get list of all categories"""
    return [category.value for category in Category]
