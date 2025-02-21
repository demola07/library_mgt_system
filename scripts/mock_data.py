import os
import sys
from datetime import date, timedelta
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Import our standalone models
from models import Base, Book, User, BorrowRecord

# Database URLs (using Docker service names)
ADMIN_DB_URL = "postgresql://admin_user:admin_password@admin_db:5432/admin_db"
FRONTEND_DB_URL = "postgresql://frontend_user:frontend_password@frontend_db:5432/frontend_db"

# Create and initialize databases
def init_db(url: str):
    engine = create_engine(url)
    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

AdminSessionLocal = init_db(ADMIN_DB_URL)
FrontendSessionLocal = init_db(FRONTEND_DB_URL)

# Sample data
BOOKS = [
    {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "isbn": "978-0132350884",
        "publisher": "Manning Publications",
        "category": "Software Development",
        "available": True
    },
    {
        "title": "Design Patterns",
        "author": "Erich Gamma",
        "isbn": "978-0201633610",
        "publisher": "Wiley",
        "category": "Software Architecture",
        "available": True
    },
    {
        "title": "The Lean Startup",
        "author": "Eric Ries",
        "isbn": "978-0307887894",
        "publisher": "O'Reilly Media",
        "category": "Business & Entrepreneurship"
    },
    {
        "title": "Steve Jobs",
        "author": "Walter Isaacson",
        "isbn": "978-1451648539",
        "publisher": "Simon & Schuster",
        "category": "Biography"
    },
    {
        "title": "A Brief History of Time",
        "author": "Stephen Hawking",
        "isbn": "978-0553380163",
        "publisher": "Bantam Books",
        "category": "Popular Science"
    },
    {
        "title": "1984",
        "author": "George Orwell",
        "isbn": "978-0451524935",
        "publisher": "Penguin Books",
        "category": "Classic Fiction"
    },
    {
        "title": "The World War II",
        "author": "Winston Churchill",
        "isbn": "978-0395416853",
        "publisher": "Houghton Mifflin",
        "category": "Military History"
    }
]

USERS = [
    {
        "email": "john.doe@example.com",
        "firstname": "John",
        "lastname": "Doe"
    },
    {
        "email": "jane.smith@example.com",
        "firstname": "Jane",
        "lastname": "Smith"
    },
    {
        "email": "bob.wilson@example.com",
        "firstname": "Bob",
        "lastname": "Wilson"
    }
]

def create_mock_data(db: Session):
    """Create mock data for testing the API"""
    print("Creating mock data...")
    
    # Create books
    print("Creating books...")
    books = []
    for book_data in BOOKS:
        book = Book(**book_data)
        db.add(book)
        books.append(book)
    
    # Create users
    print("Creating users...")
    users = []
    for user_data in USERS:
        user = User(**user_data)
        db.add(user)
        users.append(user)
    
    # Commit to get IDs
    db.commit()
    
    # Create some borrow records
    print("Creating borrow records...")
    for _ in range(3):
        book = random.choice(books)
        user = random.choice(users)
        borrow_days = random.randint(7, 30)
        
        book.available = False
        book.return_date = date.today() + timedelta(days=borrow_days)
        
        borrow_record = BorrowRecord(
            user_id=user.id,
            book_id=book.id,
            borrow_date=date.today(),
            return_date=book.return_date
        )
        db.add(borrow_record)
    
    db.commit()
    print("Mock data created successfully!")

if __name__ == "__main__":
    # Load data into admin database
    print("Loading data into admin database...")
    admin_db = AdminSessionLocal()
    try:
        create_mock_data(admin_db)
    finally:
        admin_db.close()

    # Load data into frontend database
    print("Loading data into frontend database...")
    frontend_db = FrontendSessionLocal()
    try:
        create_mock_data(frontend_db)
    finally:
        frontend_db.close()
