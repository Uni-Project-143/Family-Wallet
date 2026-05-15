import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from bson import ObjectId

from app.main import app
from app.core.dependencies import get_current_user

client = TestClient(app)

class MockUser:
    id = ObjectId("507f1f77bcf86cd799439011")

app.dependency_overrides[get_current_user] = lambda: MockUser()

class TestTransactionAPI:

    @patch("app.api.transaction.TransactionService.get_transactions", new_callable=AsyncMock)
    @patch("app.api.transaction.BankCard.find")
    @patch("app.api.transaction.GroupMembership.find_one", new_callable=AsyncMock)
    def test_get_group_transactions_success_200(self, mock_membership, mock_card_find, mock_get_tx):
        """Юзер є в групі, картки є → 200 OK і список транзакцій"""
        # 1. Мокаємо перевірку: юзер Є в групі
        mock_membership.return_value = True

        # 2. Мокаємо пошук карток: повертаємо одну фейкову картку
        mock_cursor = AsyncMock()
        mock_cursor.to_list.return_value = [MagicMock(id=ObjectId("607f1f77bcf86cd799439033"))]
        mock_card_find.return_value = mock_cursor

        # 3. Мокаємо сервіс транзакцій
        mock_get_tx.return_value = {
            "items": [], "total": 0, "page": 1, "size": 20, "pages": 1
        }

        res = client.get("/api/v1/transactions/group/607f1f77bcf86cd799439022")

        assert res.status_code == 200
        assert "items" in res.json()

    @patch("app.api.transaction.GroupMembership.find_one", new_callable=AsyncMock)
    def test_get_group_transactions_forbidden_403(self, mock_membership):
        """Юзера НЕМАЄ в групі → 403 Forbidden (Negative Path)"""
        # Мокаємо перевірку: юзера немає в групі (повертає None)
        mock_membership.return_value = None

        res = client.get("/api/v1/transactions/group/607f1f77bcf86cd799439022")

        assert res.status_code == 403
        assert res.json()["message"] == "Доступ заборонено: ви не є учасником цієї групи"
