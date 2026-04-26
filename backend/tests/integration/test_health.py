"""
Інтеграційні тести для GET /health
"""

from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestHealth:
    @patch("app.api.health.db_client")
    def test_health_returns_200_when_db_ok(self, mock_db):
        """БД доступна → 200."""
        mock_db.admin.command = AsyncMock(return_value={"ok": 1})

        res = client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "Database is healthy"

    @patch("app.api.health.db_client")
    def test_health_returns_503_when_db_down(self, mock_db):
        """БД недоступна → 503."""
        mock_db.admin.command = AsyncMock(side_effect=Exception("connection refused"))

        res = client.get("/health")
        assert res.status_code == 503
        body = res.json()
        assert body["errorCode"] == "SERVICE_UNAVAILABLE"
