from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    firstname = Column(String)
    lastname = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship with BorrowRecord
    borrow_records = relationship("BorrowRecord", back_populates="user")
