import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
class TestBookEndpoints:
    async def test_list_available_books(self, async_client: AsyncClient):
        """Test listing available books with pagination"""
        response = await async_client.get("/api/v1/books/", params={
            "page": 1,
            "limit": 10
        })
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data

    async def test_get_book_by_id(self, async_client: AsyncClient, test_book):
        """Test getting a specific book by ID"""
        response = await async_client.get(f"/api/v1/books/{test_book.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_book.id
        assert data["title"] == test_book.title

    async def test_filter_books_by_publisher(self, async_client: AsyncClient, test_book):
        """Test filtering books by publisher"""
        response = await async_client.get(
            f"/api/v1/books/publishers/{test_book.publisher}/",
            params={"page": 1, "limit": 10}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) > 0

    async def test_filter_books_by_category(self, async_client: AsyncClient, test_book):
        """Test filtering books by category"""
        response = await async_client.get(
            f"/api/v1/books/categories/{test_book.category}/",
            params={"page": 1, "limit": 10}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) > 0 