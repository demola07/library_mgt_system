from datetime import date, timedelta
import random
from sqlalchemy.orm import Session
from admin_api.app.core.database import SessionLocal
from admin_api.app.models.book import Book
from admin_api.app.models.user import User
from admin_api.app.models.borrow import BorrowRecord

# Sample data
BOOKS = [
    {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "isbn": "978-0132350884",
        "publisher": "Manning Publications",
        "category": "Software Development"
    },
    {
        "title": "Design Patterns",
        "author": "Erich Gamma",
        "isbn": "978-0201633610",
        "publisher": "Wiley",
        "category": "Software Architecture"
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
    for _ in range(3):  # Create 3 borrow records
        book = random.choice(books)
        user = random.choice(users)
        borrow_days = random.randint(7, 30)
        
        # Mark book as borrowed
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
    db = SessionLocal()
    try:
        create_mock_data(db)
    finally:
        db.close()
