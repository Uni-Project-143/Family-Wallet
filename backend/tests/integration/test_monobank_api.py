import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from bson import ObjectId
from fastapi import HTTPException, status

from app.main import app
from app.core.dependencies import get_current_user

client = TestClient(app)


# Підміна юзера для авторизації
class MockUser:
    id = ObjectId("507f1f77bcf86cd799439011")


app.dependency_overrides[get_current_user] = lambda: MockUser()


class TestMonobankAPI:

    @patch("app.api.monobank.MonobankService.connect_card", new_callable=AsyncMock)
    def test_connect_card_happy_path_200(self, mock_connect):
        """Успішне підключення картки → 200 OK"""
        mock_connect.return_value = {
            "id": "fake_card_id_123",
            "masked_pan": "•••• 1234",
            "status": "Active",
            "message": "Card connected successfully"
        }

        res = client.post(
            "/api/v1/monobank/connect",
            json={
                "group_id": "607f1f77bcf86cd799439022",
                "personal_token": "valid_mono_token"
            }
        )

        assert res.status_code == 200
        assert res.json()["masked_pan"] == "•••• 1234"

    @patch("app.api.monobank.MonobankService.connect_card", new_callable=AsyncMock)
    def test_connect_card_already_exists_409(self, mock_connect):
        """Картка вже підключена → 409 Conflict (Negative Path)"""
        # Імітуємо HTTPException, який кидає твій сервіс
        mock_connect.side_effect = HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This account is already connected to the system."
        )

        res = client.post(
            "/api/v1/monobank/connect",
            json={
                "group_id": "607f1f77bcf86cd799439022",
                "personal_token": "duplicate_token"
            }
        )

        assert res.status_code == 409
        assert "already connected" in res.json()["message"]

    @patch("app.api.monobank.MonobankService.disconnect_card", new_callable=AsyncMock)
    def test_disconnect_card_success_200(self, mock_disconnect):
        """Успішне відключення картки → 200 OK"""
        mock_disconnect.return_value = {"message": "Card permanently deleted"}

        res = client.delete("/api/v1/monobank/card/fake_card_id_123")

        assert res.status_code == 200
