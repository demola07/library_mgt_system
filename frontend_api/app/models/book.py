from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from ..core.database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    isbn = Column(String, unique=True, index=True)
    publisher = Column(String)
    category = Column(String)
    available = Column(Boolean, default=True)
    
    # Timestamp columns - commented out until database is migrated
    # created_at = Column(DateTime, server_default=func.now())
    # updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationship with BorrowRecord
    borrow_records = relationship("BorrowRecord", back_populates="book")
