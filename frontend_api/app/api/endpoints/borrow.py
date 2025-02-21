from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...core.config import settings  # Import settings where your RABBITMQ_URL is defined

from ...core.database import get_db
from ...schemas.borrow import Borrow, BorrowCreate
from ...services.book_service import BookService
from ...services.borrow_service import BorrowService
from shared.message_broker import MessageBroker

router = APIRouter()

# Dependencies to get service instances
def get_message_broker():
    return MessageBroker(rabbitmq_url=settings.RABBITMQ_URL)

def get_book_service(message_broker: MessageBroker = Depends(get_message_broker)):
    return BookService(message_broker)

def get_borrow_service(message_broker: MessageBroker = Depends(get_message_broker)):
    return BorrowService(message_broker)

@router.post("/user/{user_id}/book/{book_id}",
    response_model=Borrow,
    summary="Borrow a book",
    status_code=201,
    responses={
        404: {"description": "Book is not available or found"},
    }
)
async def borrow_book(  # Make the endpoint async
    user_id: int,  # Path parameter from URL
    book_id: int,  # Path parameter from URL
    days: int,     # Query parameter (?days=7)
    db: Session = Depends(get_db),
    book_service: BookService = Depends(get_book_service),
    borrow_service: BorrowService = Depends(get_borrow_service)
):
    """Borrow a book for a specified number of days."""
    # Check if book exists and is available
    book = book_service.get_book(db, book_id=book_id)
    if not book or not book.available:
        raise HTTPException(
            status_code=404,
            detail="Book is not available or found"
        )
    
    # Create borrow record
    borrow_data = BorrowCreate(
        user_id=user_id,
        book_id=book_id,
        days=days
    )
    
    try:
        # Use await with the async function
        return await borrow_service.create_borrow_record(db=db, borrow=borrow_data)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
