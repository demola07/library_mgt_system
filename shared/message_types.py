from enum import Enum

class MessageType(Enum):
    BOOKS_CREATED = "books.created"    # Admin API -> Frontend API
    BOOK_DELETED = "book.deleted"    # Admin API -> Frontend API
    BOOK_BORROWED = "book.borrowed"  # Frontend API -> Admin API
    USER_CREATED = "user.created"  # Frontend API -> Admin API