import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.exceptions import UserAlreadyExistsError, InvalidCredentialsError

client = TestClient(app)

# ════════════════════════════════════════════════════════════════════════════
# POST /api/v1/auth/register
# ════════════════════════════════════════════════════════════════════════════

class TestRegister:
    @patch("app.api.auth.AuthService.register", new_callable=AsyncMock)
    def test_register_happy_path_returns_201_with_token(self, mock_register):
        """Новий email → 201 + access_token у відповіді."""
        mock_register.return_value = {
            "access_token": "fake-jwt-token-123",
            "token_type": "bearer",
            "user": {
                "id": "507f1f77bcf86cd799439011",
                "email": "new@example.com",
                "fullName": "Новий Користувач",  # <-- ВИПРАВЛЕНО НА fullName
                "avatar_url": None
            }
        }

        res = client.post(
            "/api/v1/auth/register",
            json={
                "email": "new@example.com",
                "password": "StrongPass1!",
                "confirmPassword": "StrongPass1!",
                "fullName": "Новий Користувач",
            },
        )

        assert res.status_code == 201
        body = res.json()
        assert "access_token" in body
        assert body["access_token"] == "fake-jwt-token-123"

    @patch("app.api.auth.AuthService.register", new_callable=AsyncMock)
    def test_register_duplicate_email_returns_409(self, mock_register):
        """Email вже існує → 409 Conflict."""
        # Імітуємо ситуацію, коли сервіс викидає нашу кастомну помилку
        mock_register.side_effect = UserAlreadyExistsError()

        res = client.post(
            "/api/v1/auth/register",
            json={
                "email": "taken@example.com",
                "password": "StrongPass1!",
                "confirmPassword": "StrongPass1!",
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
    @patch("app.api.auth.AuthService.login", new_callable=AsyncMock)
    def test_login_happy_path_returns_200_with_token(self, mock_login):
        """Правильні credentials → 200 + access_token."""
        mock_login.return_value = {
            "access_token": "fake-jwt-token-123",
            "token_type": "bearer",
            "user": {
                "id": "507f1f77bcf86cd799439011",
                "email": "test@example.com",
                "fullName": "Test User",  # <-- ВИПРАВЛЕНО НА fullName
                "avatar_url": None
            }
        }

        res = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "correct-password"},
        )
        assert res.status_code == 200
        body = res.json()
        assert "access_token" in body

    @patch("app.api.auth.AuthService.login", new_callable=AsyncMock)
    def test_login_wrong_credentials_returns_401(self, mock_login):
        """Невірний email або пароль → 401."""
        mock_login.side_effect = InvalidCredentialsError()

        res = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "wrong-password"},
        )
        assert res.status_code == 401

    def test_login_missing_password_returns_422(self):
        res = client.post("/api/v1/auth/login", json={"email": "a@b.com"})
        assert res.status_code == 422

    def test_login_empty_body_returns_422(self):
        res = client.post("/api/v1/auth/login", json={})
        assert res.status_code == 422
