from sqlalchemy import Column, Integer, String, Boolean, Date, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
import enum
from datetime import date

class Category(str, enum.Enum):
    FICTION = "fiction"
    TECHNOLOGY = "technology"
    SCIENCE = "science"
    BUSINESS = "business"
    HISTORY = "history"
    BIOGRAPHY = "biography"

class Publisher(str, enum.Enum):
    WILEY = "wiley"
    APRESS = "apress"
    MANNING = "manning"
    OREILLY = "oreilly"
    PACKT = "packt"

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    isbn = Column(String, unique=True, index=True)
    publisher = Column(Enum(Publisher), index=True)
    category = Column(Enum(Category), index=True)
    available = Column(Boolean, default=True)
    return_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship with BorrowRecord
    borrow_records = relationship("BorrowRecord", back_populates="book")
