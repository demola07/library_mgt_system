from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...schemas.book import Book, BookCreate, BookBorrowed
from ...services import book_service

router = APIRouter()

@router.post("/batch", response_model=list[Book], summary="Add multiple books to catalogue")
def create_books(books: BooksCreate, db: Session = Depends(get_db)):
    """Add multiple books to the catalogue at once"""
    return book_service.create_books(db=db, books=books.books)

@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """Remove a book from the catalogue"""
    if not book_service.delete_book(db=db, book_id=book_id):
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted successfully"}

@router.get("/unavailable/", response_model=List[UnavailableBook])
def get_unavailable_books(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all books that are currently borrowed, showing when they will be available"""
    books = book_service.get_unavailable_books(db=db, skip=skip, limit=limit)
    
    # Transform to UnavailableBook format
    return [
        UnavailableBook(
            id=book.id,
            title=book.title,
            author=book.author,
            isbn=book.isbn,
            publisher=book.publisher,
            category=book.category,
            borrower_name=f"{book.borrow_records[0].user.firstname} {book.borrow_records[0].user.lastname}",
            borrower_email=book.borrow_records[0].user.email,
            return_date=book.return_date
        ) for book in books
    ]
