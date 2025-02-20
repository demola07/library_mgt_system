from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...schemas.book import Book, BookCreate, BookBorrowed
from ...services import book_service

router = APIRouter()

@router.post("/", response_model=Book)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    """Add a new book to the catalogue"""
    return book_service.create_book(db=db, book=book)

@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """Remove a book from the catalogue"""
    if not book_service.delete_book(db=db, book_id=book_id):
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted successfully"}

@router.get("/unavailable/", response_model=List[Book])
def get_unavailable_books(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all books that are currently borrowed"""
    return book_service.get_unavailable_books(db=db, skip=skip, limit=limit)
