from sqlalchemy.orm import Session
from ..models.book import Book
from ..schemas.book import BookCreate, BookUpdate
from ..core.redis import publish_book_update

def create_book(db: Session, book: BookCreate) -> Book:
    db_book = Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    
    # Publish to Redis for frontend service
    publish_book_update(book.model_dump(), 'create')
    
    return db_book

def delete_book(db: Session, book_id: int) -> bool:
    book = db.query(Book).filter(Book.id == book_id).first()
    if book:
        # Publish to Redis for frontend service
        publish_book_update({'id': book_id}, 'delete')
        
        db.delete(book)
        db.commit()
        return True
    return False

def get_book(db: Session, book_id: int) -> Book:
    return db.query(Book).filter(Book.id == book_id).first()

def get_unavailable_books(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(Book)
        .filter(Book.available == False)
        .offset(skip)
        .limit(limit)
        .all()
    )
