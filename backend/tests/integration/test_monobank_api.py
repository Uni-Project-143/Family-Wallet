import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from bson import ObjectId
from fastapi import HTTPException, status

from app.main import app
from app.core.dependencies import get_current_user
from app.models.bank_card import BankCard

client = TestClient(app)


class MockUser:
    id = ObjectId("507f1f77bcf86cd799439011")


app.dependency_overrides[get_current_user] = lambda: MockUser()


class TestMonobankAPI:

    # 1. Фікс для тесту, що повертав 400
    @patch("app.api.monobank.httpx.AsyncClient.post", new_callable=AsyncMock)
    def test_connect_card_happy_path_200(self, mock_post):
        """Успішне підключення картки → 200 OK"""
        # Мокаємо успішну відповідь від реального Монобанку
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        with patch.object(BankCard, "account_id", "account_id", create=True), \
            patch("app.api.monobank.BankCard.find_one", new_callable=AsyncMock) as mock_find_one, \
            patch("app.api.monobank.BankCard.insert", new_callable=AsyncMock) as mock_insert:
            mock_find_one.return_value = None  # Картки ще немає в БД
            mock_insert.return_value = None  # Імітуємо успішне збереження

            res = client.post(
                "/api/v1/monobank/connect",
                json={
                    "group_id": "607f1f77bcf86cd799439022",
                    "personal_token": "valid_mono_token",
                    "account_id": "mono_acc_12345",
                    "masked_pan": "•••• 1234",
                    "balance": 1500.00
                }
            )

            assert res.status_code == 200

    # 2. Фікс для KeyError: 'detail'
    def test_connect_card_already_exists_409(self):
        """Картка вже підключена → 409 Conflict (Negative Path)"""
        with patch.object(BankCard, "account_id", "account_id", create=True), \
            patch("app.api.monobank.BankCard.find_one", new_callable=AsyncMock) as mock_find_one:
            mock_find_one.return_value = MagicMock()  # Картка вже є

            res = client.post(
                "/api/v1/monobank/connect",
                json={
                    "group_id": "607f1f77bcf86cd799439022",
                    "personal_token": "duplicate_token",
                    "account_id": "mono_acc_12345",
                    "masked_pan": "•••• 1234",
                    "balance": 1500.00
                }
            )

            assert res.status_code == 409
            # ВИПРАВЛЕНО: Глобальний хендлер тепер повертає "message", а не "detail"
            assert "already connected" in res.json()["message"]

