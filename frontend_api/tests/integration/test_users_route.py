import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
class TestUserEndpoints:
    async def test_create_user(self, async_client: AsyncClient):
        """Test creating a new user"""
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "email": f"test{unique_id}@example.com",
            "firstname": "Test",
            "lastname": "User"
        }
        response = await async_client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["firstname"] == user_data["firstname"]
        assert data["lastname"] == user_data["lastname"]

    async def test_create_duplicate_user(self, async_client: AsyncClient, test_user):
        """Test creating a user with existing email"""
        user_data = {
            "email": test_user.email,
            "firstname": "Another",
            "lastname": "User"
        }
        response = await async_client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower() 