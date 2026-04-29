"""
Інтеграційні тести для /api/v1/groups/* (create_group, generate_invite, join_group)
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from bson import ObjectId
from fastapi.testclient import TestClient

from app.main import app
from app.core.dependencies import get_current_user
from app.core.security import create_access_token

client = TestClient(app)


# ── Фабрики ───────────────────────────────────────────────────────────────


def make_user(user_id: str = "507f1f77bcf86cd799439011") -> MagicMock:
    user = MagicMock()
    user.id = ObjectId(user_id)
    user.email = "admin@example.com"
    user.full_name = "Admin User"
    return user


def make_membership(role: str = "ADMIN") -> MagicMock:
    m = MagicMock()
    m.role = role
    m.user_id = ObjectId("507f1f77bcf86cd799439011")
    m.group_id = ObjectId("617f1f77bcf86cd799439022")
    return m


def make_invite(expired: bool = False) -> MagicMock:
    invite = MagicMock()
    invite.token = "a3f1c2d4e5b6a7f8c9d0e1f2a3b4c5d6"
    invite.group_id = ObjectId("617f1f77bcf86cd799439022")
    if expired:
        invite.expires_at = datetime.utcnow() - timedelta(hours=1)
    else:
        invite.expires_at = datetime.utcnow() + timedelta(hours=47)
    invite.save = AsyncMock()
    return invite


def auth_headers(user_id: str = "507f1f77bcf86cd799439011") -> dict:
    """Повертає Bearer-заголовок з валідним JWT."""
    token = create_access_token(user_id)
    return {"Authorization": f"Bearer {token}"}


# ── Dependency override: підміна get_current_user ─────────────────────────


def override_get_current_user(user_id: str = "507f1f77bcf86cd799439011"):
    """Повертає фейкового юзера без звернення до БД."""
    async def _override():
        return make_user(user_id)
    return _override


# ════════════════════════════════════════════════════════════════════════════
# POST /api/v1/groups/
# ════════════════════════════════════════════════════════════════════════════


class TestCreateGroup:
    def setup_method(self):
        app.dependency_overrides[get_current_user] = override_get_current_user()

    def teardown_method(self):
        app.dependency_overrides.clear()

    @patch("app.api.group.GroupMembership.insert", new_callable=AsyncMock)
    def test_create_group_happy_path_returns_201(self, mock_membership_insert):
        with patch("app.api.group.Group") as MockGroup:
            instance = MagicMock()
            instance.id = ObjectId("617f1f77bcf86cd799439022")
            instance.name = "Родина Петренків"
            instance.insert = AsyncMock()
            MockGroup.return_value = instance

            res = client.post(
                "/api/v1/groups/",
                headers=auth_headers(),
                json={"name": "Родина Петренків"},
            )

        assert res.status_code == 201
        body = res.json()
        assert "group_id" in body
        assert body["name"] == "Родина Петренків"

    def test_create_group_no_auth_returns_403(self):
        """Без токена → 403 (HTTPBearer повертає 403)."""
        app.dependency_overrides.clear()
        res = client.post("/api/v1/groups/", json={"name": "Test"})
        assert res.status_code == 403

    def test_create_group_missing_name_returns_422(self):
        res = client.post("/api/v1/groups/", headers=auth_headers(), json={})
        assert res.status_code == 422


# ════════════════════════════════════════════════════════════════════════════
# GET /api/v1/groups/{group_id}/invite
# ════════════════════════════════════════════════════════════════════════════


class TestGenerateInviteLink:
    def setup_method(self):
        app.dependency_overrides[get_current_user] = override_get_current_user()

    def teardown_method(self):
        app.dependency_overrides.clear()

    @patch("app.api.group.InviteToken.insert", new_callable=AsyncMock)
    @patch("app.api.group.GroupMembership.find_one", new_callable=AsyncMock)
    def test_admin_gets_invite_link(self, mock_find_one, mock_insert):
        """ADMIN-учасник → 200 + invite_link."""
        mock_find_one.return_value = make_membership(role="ADMIN")
        new_invite = make_invite()
        mock_insert.return_value = new_invite

        with patch("app.api.group.InviteToken") as MockInvite:
            instance = MagicMock()
            instance.token = "a3f1c2d4e5b6a7f8c9d0e1f2a3b4c5d6"
            instance.expires_at = datetime.utcnow() + timedelta(hours=47)
            instance.insert = AsyncMock()
            MockInvite.return_value = instance

            res = client.get(
                "/api/v1/groups/617f1f77bcf86cd799439022/invite",
                headers=auth_headers(),
            )

        assert res.status_code == 200
        body = res.json()
        assert "invite_link" in body
        assert "/join/" in body["invite_link"]

    @patch("app.api.group.GroupMembership.find_one", new_callable=AsyncMock)
    def test_member_cannot_generate_invite_returns_403(self, mock_find_one):
        """MEMBER (не ADMIN) → 403."""
        mock_find_one.return_value = make_membership(role="MEMBER")

        res = client.get(
            "/api/v1/groups/617f1f77bcf86cd799439022/invite",
            headers=auth_headers(),
        )
        assert res.status_code == 403

    @patch("app.api.group.GroupMembership.find_one", new_callable=AsyncMock)
    def test_non_member_cannot_generate_invite_returns_403(self, mock_find_one):
        """Не-учасник групи → 403."""
        mock_find_one.return_value = None

        res = client.get(
            "/api/v1/groups/617f1f77bcf86cd799439022/invite",
            headers=auth_headers(),
        )
        assert res.status_code == 403

    def test_invalid_group_id_format_returns_400(self):
        """Невалідний ObjectId → 400."""
        res = client.get(
            "/api/v1/groups/not-a-valid-id/invite",
            headers=auth_headers(),
        )
        assert res.status_code == 400


# ════════════════════════════════════════════════════════════════════════════
# POST /api/v1/groups/join
# ════════════════════════════════════════════════════════════════════════════


class TestJoinGroup:
    def setup_method(self):
        app.dependency_overrides[get_current_user] = override_get_current_user()

    def teardown_method(self):
        app.dependency_overrides.clear()

    @patch("app.api.group.GroupMembership.insert", new_callable=AsyncMock)
    @patch("app.api.group.GroupMembership.find_one", new_callable=AsyncMock)
    @patch("app.api.group.InviteToken.find_one", new_callable=AsyncMock)
    def test_join_happy_path_returns_200(
        self, mock_invite_find, mock_member_find, mock_member_insert
    ):
        """Валідний невикористаний токен → 200."""
        mock_invite_find.return_value = make_invite(expired=False)
        mock_member_find.return_value = None  # ще не учасник

        res = client.post(
            "/api/v1/groups/join",
            headers=auth_headers(),
            json={"invite_link": "https://family-wallet.com/join/a3f1c2d4e5b6a7f8c9d0e1f2a3b4c5d6"},
        )
        assert res.status_code == 200

    @patch("app.api.group.InviteToken.find_one", new_callable=AsyncMock)
    def test_join_expired_invite_returns_410(self, mock_invite_find):
        """Протермінований токен → 410 Gone."""
        mock_invite_find.return_value = make_invite(expired=True)

        res = client.post(
            "/api/v1/groups/join",
            headers=auth_headers(),
            json={"invite_link": "https://family-wallet.com/join/a3f1c2d4e5b6a7f8c9d0e1f2a3b4c5d6"},
        )
        assert res.status_code == 410

    @patch("app.api.group.InviteToken.find_one", new_callable=AsyncMock)
    def test_join_invalid_token_returns_400(self, mock_invite_find):
        """Токен не знайдено в БД → 400."""
        mock_invite_find.return_value = None

        res = client.post(
            "/api/v1/groups/join",
            headers=auth_headers(),
            json={"invite_link": "https://family-wallet.com/join/nonexistent-token"},
        )
        assert res.status_code == 400

    @patch("app.api.group.GroupMembership.find_one", new_callable=AsyncMock)
    @patch("app.api.group.InviteToken.find_one", new_callable=AsyncMock)
    def test_join_already_member_returns_400(self, mock_invite_find, mock_member_find):
        """Вже учасник → 400."""
        mock_invite_find.return_value = make_invite(expired=False)
        mock_member_find.return_value = make_membership()  # вже є

        res = client.post(
            "/api/v1/groups/join",
            headers=auth_headers(),
            json={"invite_link": "https://family-wallet.com/join/a3f1c2d4e5b6a7f8c9d0e1f2a3b4c5d6"},
        )
        assert res.status_code == 400

    def test_join_invalid_invite_link_format_returns_400(self):
        """Невалідний URL (без /join/) → 400 від _extract_token_from_link."""
        res = client.post(
            "/api/v1/groups/join",
            headers=auth_headers(),
            json={"invite_link": "https://family-wallet.com/groups/abc"},
        )
        assert res.status_code == 400

    def test_join_missing_invite_link_returns_422(self):
        res = client.post("/api/v1/groups/join", headers=auth_headers(), json={})
        assert res.status_code == 422
