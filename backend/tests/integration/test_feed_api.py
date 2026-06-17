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


class TestFeedAPI:

    @patch("app.api.feed.GiftEvent")
    @patch("app.api.feed.GroupMembership.find_one", new_callable=AsyncMock)
    @patch("app.api.feed.Transaction.find")
    def test_get_feed_happy_path_200(self, mock_tx_find, mock_membership, mock_gift_event):
        """Позитивний сценарій: Юзер є в групі, отримуємо стрічку транзакцій (200 OK)"""
        mock_membership.return_value = True

        mock_find_query = MagicMock()
        mock_find_query.count = AsyncMock(return_value=1)

        mock_sort = MagicMock()
        mock_skip = MagicMock()
        mock_limit = MagicMock()

        mock_find_query.sort.return_value = mock_sort
        mock_sort.skip.return_value = mock_skip
        mock_skip.limit.return_value = mock_limit

        fake_tx = MagicMock(
            id=ObjectId("607f1f77bcf86cd799439022"),
            amount=150.50,
            currency="UAH",
            description="Купівля продуктів",
            timestamp="2026-05-15T12:00:00Z",
            card_id=None,
            category_id=None,
            is_secret_gift=False,
            reactions=[]  # ВАЖЛИВО: для Counter(r.emoji for r in tx.reactions)
        )
        mock_limit.to_list = AsyncMock(return_value=[fake_tx])
        mock_tx_find.return_value = mock_find_query

        # ВАЖЛИВО: Правильний мок для GiftEvent.find(...).to_list()
        mock_gift_event.target_user_id = "mock_target_id"
        mock_gift_event.status = "mock_status"
        mock_gift_query = MagicMock()
        mock_gift_query.to_list = AsyncMock(return_value=[])
        mock_gift_event.find.return_value = mock_gift_query

        res = client.get("/api/v1/feed/607f1f77bcf86cd799439033")

        assert res.status_code == 200
        data = res.json()
        assert "items" in data
        assert len(data["items"]) == 1
        assert data["items"][0]["description"] == "Купівля продуктів"

    @patch("app.api.feed.GroupMembership.find_one", new_callable=AsyncMock)
    def test_get_feed_forbidden_403(self, mock_membership):
        """Negative AC: Юзера немає в групі → 403 Forbidden"""
        mock_membership.return_value = None
        res = client.get("/api/v1/feed/607f1f77bcf86cd799439033")
        assert res.status_code == 403
        assert res.json()[
                   "message"] == "Ви не є учасником цієї групи"  # <-- ЗМІНЕНО detail на message

    def test_get_feed_invalid_group_id_400(self):
        """Negative AC: Передано невалідний ObjectID → 400 Bad Request"""
        res = client.get("/api/v1/feed/not-a-valid-mongo-id")
        assert res.status_code == 400
        assert "Невалідний ID групи" in res.json()["message"]  # <-- ЗМІНЕНО detail на message
