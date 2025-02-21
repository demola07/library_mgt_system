from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...schemas.book import Book, BookCreate, BookBorrowed, BooksCreate, UnavailableBook, BookUpdate
from ...services.book_service import book_service
from shared.pagination import PaginatedResponse

router = APIRouter()

@router.post("/bulk", response_model=List[Book])
async def add_books(
    books: List[BookCreate],
    db: Session = Depends(get_db)
):
    """Add multiple books to the catalogue"""
    return await book_service.create_books(db=db, books=books)

@router.delete("/{book_id}")
async def remove_book(
    book_id: int,
    db: Session = Depends(get_db)
):
    """Remove a book from the catalogue"""
    success = await book_service.delete_book(db=db, book_id=book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted successfully"}

@router.get("/unavailable", response_model=PaginatedResponse[UnavailableBook])
async def list_unavailable_books(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """List all books that are currently unavailable with pagination
    
    Args:
        page: Page number (1-based)
        limit: Maximum number of items per page
        db: Database session
    """
    return await book_service.get_unavailable_books(db=db, page=page, limit=limit)
