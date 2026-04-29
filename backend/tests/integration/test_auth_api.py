"""
Інтеграційні тести для /api/v1/auth/* (register, login)

Мокуємо реальні виклики: User.find_one, User.insert
через unittest.mock.patch — патчимо саме те місце, де
функція використовується (app.api.auth), а не де визначена.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.core.security import get_password_hash

client = TestClient(app)

# ── Фабрика фейкового User-документа ─────────────────────────────────────


def make_user(
    user_id: str = "507f1f77bcf86cd799439011",
    email: str = "test@example.com",
    full_name: str = "Test User",
    password: str = "password123",
) -> MagicMock:
    user = MagicMock()
    user.id = user_id
    user.email = email
    user.full_name = full_name
    user.hashed_password = get_password_hash(password)
    return user


# ════════════════════════════════════════════════════════════════════════════
# POST /api/v1/auth/register
# ════════════════════════════════════════════════════════════════════════════


class TestRegister:
    @patch("app.api.auth.User.find_one", new_callable=AsyncMock)
    @patch("app.api.auth.User.insert", new_callable=AsyncMock)
    def test_register_happy_path_returns_201_with_token(self, mock_insert, mock_find_one):
        """Новий email → 201 + access_token у відповіді."""
        mock_find_one.return_value = None  # email вільний

        new_user = make_user(email="new@example.com")
        mock_insert.return_value = new_user

        # Патчимо insert на рівні екземпляра через side_effect
        with patch("app.api.auth.User") as MockUser:
            instance = MagicMock()
            instance.id = "507f1f77bcf86cd799439011"
            instance.insert = AsyncMock(return_value=None)
            MockUser.find_one = AsyncMock(return_value=None)
            MockUser.return_value = instance

            res = client.post(
                "/api/v1/auth/register",
                json={
                    "email": "new@example.com",
                    "password": "StrongPass1!",
                    "fullName": "Новий Користувач",
                },
            )

        assert res.status_code == 201
        body = res.json()
        assert "access_token" in body
        assert isinstance(body["access_token"], str)
        assert len(body["access_token"]) > 20

    @patch("app.api.auth.User.find_one", new_callable=AsyncMock)
    def test_register_duplicate_email_returns_409(self, mock_find_one):
        """Email вже існує → 409 Conflict."""
        mock_find_one.return_value = make_user(email="taken@example.com")

        res = client.post(
            "/api/v1/auth/register",
            json={
                "email": "taken@example.com",
                "password": "StrongPass1!",
                "fullName": "Duplicate User",
            },
        )
        assert res.status_code == 409

    def test_register_missing_email_returns_422(self):
        """Відсутній email → 422 Validation Error."""
        res = client.post(
            "/api/v1/auth/register",
            json={"password": "pass123", "fullName": "No Email"},
        )
        assert res.status_code == 422

    def test_register_missing_password_returns_422(self):
        res = client.post(
            "/api/v1/auth/register",
            json={"email": "a@b.com", "fullName": "No Pass"},
        )
        assert res.status_code == 422

    def test_register_invalid_email_format_returns_422(self):
        """Невалідний email → 422 (pydantic EmailStr)."""
        res = client.post(
            "/api/v1/auth/register",
            json={"email": "not-an-email", "password": "pass123", "fullName": "Bad Email"},
        )
        assert res.status_code == 422


# ════════════════════════════════════════════════════════════════════════════
# POST /api/v1/auth/login
# ════════════════════════════════════════════════════════════════════════════


class TestLogin:
    @patch("app.api.auth.User.find_one", new_callable=AsyncMock)
    def test_login_happy_path_returns_200_with_token(self, mock_find_one):
        """Правильні credentials → 200 + access_token."""
        mock_find_one.return_value = make_user(
            email="test@example.com", password="correct-password"
        )

        res = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "correct-password"},
        )
        assert res.status_code == 200
        body = res.json()
        assert "access_token" in body
        assert isinstance(body["access_token"], str)

    @patch("app.api.auth.User.find_one", new_callable=AsyncMock)
    def test_login_wrong_password_returns_401(self, mock_find_one):
        """Правильний email, невірний пароль → 401."""
        mock_find_one.return_value = make_user(password="real-password")

        res = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "wrong-password"},
        )
        assert res.status_code == 401

    @patch("app.api.auth.User.find_one", new_callable=AsyncMock)
    def test_login_unknown_email_returns_401(self, mock_find_one):
        """Неіснуючий email → 401 (не 404, щоб не розкривати наявність акаунта)."""
        mock_find_one.return_value = None

        res = client.post(
            "/api/v1/auth/login",
            json={"email": "ghost@example.com", "password": "any"},
        )
        assert res.status_code == 401

    def test_login_missing_password_returns_422(self):
        res = client.post("/api/v1/auth/login", json={"email": "a@b.com"})
        assert res.status_code == 422

    def test_login_empty_body_returns_422(self):
        res = client.post("/api/v1/auth/login", json={})
        assert res.status_code == 422
