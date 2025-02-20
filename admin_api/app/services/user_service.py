from sqlalchemy.orm import Session
from typing import List
from ..models.user import User
from ..models.borrow import BorrowRecord
from ..schemas.book import BookBorrowed

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

def get_user_with_borrowed_books(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users_with_borrowed_books(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(User)
        .join(BorrowRecord)
        .offset(skip)
        .limit(limit)
        .all()
    )
