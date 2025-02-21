import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
class TestBorrowEndpoints:
    async def test_borrow_book_success(self, async_client: AsyncClient, test_book, test_user):
        """Test successfully borrowing a book"""
        response = await async_client.post(
            f"/api/v1/borrow/user/{test_user.id}/book/{test_book.id}",
            params={"days": 7}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == test_user.id
        assert data["book_id"] == test_book.id

    async def test_borrow_unavailable_book(self, async_client: AsyncClient, borrowed_test_book, test_user):
        """Test attempting to borrow an unavailable book"""
        response = await async_client.post(
            f"/api/v1/borrow/user/{test_user.id}/book/{borrowed_test_book.id}",
            params={"days": 7}
        )
        assert response.status_code == 404
        assert "not available" in response.json()["detail"].lower() 