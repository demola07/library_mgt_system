from typing import TypeVar, Generic, List
from pydantic import BaseModel

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic schema for paginated responses.
    
    This is a shared schema used by both admin_api and frontend_api
    for consistent pagination handling across the application.
    
    Attributes:
        items: List of items for the current page
        total: Total number of items across all pages
        page: Current page number (1-based)
        limit: Maximum number of items per page
        pages: Total number of pages
    """
    items: List[T]
    total: int
    page: int
    limit: int
    pages: int

    @classmethod
    def create(cls, items: List[T], total: int, page: int, limit: int) -> "PaginatedResponse[T]":
        """Helper method to create a paginated response.
        
        Args:
            items: The items for the current page
            total: Total number of items
            page: Current page number
            limit: Maximum items per page
            
        Returns:
            A PaginatedResponse instance
        """
        return cls(
            items=items,
            total=total,
            page=page,
            limit=limit,
            pages=((total - 1) // limit) + 1 if total > 0 else 0
        ) 