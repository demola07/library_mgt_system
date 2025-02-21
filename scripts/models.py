from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    isbn = Column(String, unique=True, index=True)
    publisher = Column(String)
    category = Column(String)
    available = Column(Boolean, default=True)
    return_date = Column(Date, nullable=True)

    borrow_records = relationship("BorrowRecord", back_populates="book")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    firstname = Column(String)
    lastname = Column(String)

    borrow_records = relationship("BorrowRecord", back_populates="user")

class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    borrow_date = Column(Date)
    return_date = Column(Date)

    user = relationship("User", back_populates="borrow_records")
    book = relationship("Book", back_populates="borrow_records") 