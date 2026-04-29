"""
conftest.py — спільна конфігурація для всього тестового suite.

Відключає реальне підключення до Beanie/MongoDB при старті FastAPI,
щоб TestClient не вимагав живої бази.
"""

import pytest
from unittest.mock import AsyncMock, patch


@pytest.fixture(scope="session", autouse=True)
def disable_beanie_init():
    """Перехоплює beanie.init_beanie при startup FastAPI."""
    with patch("beanie.init_beanie", new_callable=AsyncMock):
        yield


@pytest.fixture(scope="session", autouse=True)
def disable_db_connection():
    """Перехоплює підключення до MongoDB Atlas при старті."""
    with patch("app.config.database.AsyncIOMotorClient"):
        yield
