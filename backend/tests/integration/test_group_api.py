import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from bson import ObjectId

from app.main import app
from app.core.dependencies import get_current_user

client = TestClient(app)

# 1. Створюємо фейкового юзера для обходу авторизації
class MockUser:
    id = ObjectId("507f1f77bcf86cd799439011")

async def override_get_current_user():
    return MockUser()

# Підміняємо реальну перевірку токена на нашого фейкового юзера
app.dependency_overrides[get_current_user] = override_get_current_user

class TestGroupEndpoints:

    @patch("app.api.group.GroupService.create_group", new_callable=AsyncMock)
    def test_create_group_endpoint_201(self, mock_create):
        """Перевіряємо, що ендпоінт створення групи віддає статус 201"""
        # Кажемо моку, що має повернути сервіс
        mock_create.return_value = {"message": "Success", "group_id": "123", "name": "Test Family"}

        # Робимо HTTP запит
        response = client.post("/api/v1/group/", json={"name": "Test Family"})

        assert response.status_code == 201
        assert response.json()["name"] == "Test Family"

    @patch("app.api.group.GroupService.regenerate_invite_link", new_callable=AsyncMock)
    def test_regenerate_invite_endpoint_200(self, mock_regenerate):
        """Перевіряємо ендпоінт твоєї задачі PROJ-234"""
        mock_regenerate.return_value = {
            "invite_link": "https://family-wallet.com/join/new-token",
            "token": "new-token",
            "expires_at": "2026-05-01T00:00:00"
        }

        group_id = str(ObjectId())
        response = client.post(f"/api/v1/group/{group_id}/invite/regenerate")

        assert response.status_code == 200
        assert response.json()["token"] == "new-token"

    def test_create_group_missing_name_422(self):
        """Перевіряємо Pydantic валідацію (якщо не передали name)"""
        response = client.post("/api/v1/group/", json={})

        # FastAPI має автоматично відбити запит із 422 Unprocessable Entity
        assert response.status_code == 422



    @patch("app.api.group.GroupService.get_user_groups", new_callable=AsyncMock)
    def test_get_my_groups_returns_200(self, mock_get_groups):
        """Перевіряємо отримання списку своїх груп"""
        # Імітуємо відповідь сервісу
        mock_get_groups.return_value = [
            {"id": "607f1f77bcf86cd799439011", "name": "Моя Сім'я", "role": "ADMIN"}
        ]

        response = client.get("/api/v1/group/me")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Моя Сім'я"

    @patch("app.api.group.GroupService.join_group", new_callable=AsyncMock)
    def test_join_group_success_200(self, mock_join):
        """Перевіряємо успішне приєднання до групи за лінкою"""
        mock_join.return_value = {"message": "You have successfully joined the family!"}

        response = client.post(
            "/api/v1/group/join",
            json={"invite_link": "https://family-wallet.com/join/valid-token-123"}
        )

        assert response.status_code == 200
        assert "successfully joined" in response.json()["message"]
