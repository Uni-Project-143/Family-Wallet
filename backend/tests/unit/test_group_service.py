import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from bson import ObjectId

# 🚀 ЧИТ-КОД: Вимикаємо перевірку підключення до БД глибоко в ядрі Beanie
from beanie.odm.documents import Document
patch.object(Document, "get_pymongo_collection", return_value=MagicMock()).start()

from app.services.group_service import GroupService
from app.exceptions import InvalidInviteError, InviteExpiredError

# Допоміжний фейковий токен
class MockInvite:
    def __init__(self, expired=False):
        self.group_id = ObjectId()
        self.token = "valid-token-123"
        self.expires_at = datetime.utcnow() - timedelta(days=1) if expired else datetime.utcnow() + timedelta(days=1)

# Бронебійні фейкові класи для імітації сесій MongoDB
class DummyTransaction:
    async def __aenter__(self): return self
    async def __aexit__(self, exc_type, exc, tb): pass

class DummySession:
    async def __aenter__(self): return self
    async def __aexit__(self, exc_type, exc, tb): pass
    def start_transaction(self): return DummyTransaction()

class DummyDbClient:
    async def start_session(self, *args, **kwargs):
        return DummySession()

# Глобальний фейковий клієнт БД
dummy_db = DummyDbClient()

@pytest.mark.asyncio
class TestGroupService:

    @patch("app.services.group_service.GroupRepository.get_membership", new_callable=AsyncMock)
    @patch("app.services.group_service.GroupRepository.add_member", new_callable=AsyncMock)
    @patch("app.services.group_service.InviteRepository.save", new_callable=AsyncMock)
    @patch("app.services.group_service.InviteRepository.get_by_token", new_callable=AsyncMock)
    @patch("app.services.group_service.db_client", new=dummy_db)
    async def test_join_group_happy_path(self, mock_get_invite, mock_save, mock_add_member, mock_get_membership):
        mock_get_invite.return_value = MockInvite(expired=False)
        mock_get_membership.return_value = None

        result = await GroupService.join_group("https://family-wallet.com/join/valid-token-123", ObjectId())

        assert result["message"] == "You have successfully joined the family!"
        mock_add_member.assert_called_once()
        mock_save.assert_called_once()

    @patch("app.services.group_service.InviteRepository.get_by_token", new_callable=AsyncMock)
    async def test_join_group_expired_token(self, mock_get_invite):
        mock_get_invite.return_value = MockInvite(expired=True)

        with pytest.raises(InviteExpiredError):
            await GroupService.join_group("https://family-wallet.com/join/valid-token-123", ObjectId())

    @patch("app.services.group_service.InviteRepository.get_by_token", new_callable=AsyncMock)
    async def test_join_group_invalid_format(self, mock_get_invite):
        with pytest.raises(InvalidInviteError) as exc:
            await GroupService.join_group("just-a-random-string", ObjectId())
        assert "Invalid invite link structure" in str(exc.value.detail)

    @patch("app.services.group_service.GroupRepository.create_group", new_callable=AsyncMock)
    @patch("app.services.group_service.GroupRepository.add_member", new_callable=AsyncMock)
    @patch("app.services.group_service.db_client", new=dummy_db)
    async def test_create_group_happy_path(self, mock_add_member, mock_create_group):
        user_id = ObjectId()
        result = await GroupService.create_group("Test Family", user_id)

        assert result["message"] == "Group created successfully"
        assert result["name"] == "Test Family"
        mock_create_group.assert_called_once()
        mock_add_member.assert_called_once()

    @patch("app.services.group_service.GroupRepository.get_user_memberships", new_callable=AsyncMock)
    @patch("app.services.group_service.GroupRepository.get_groups_by_ids", new_callable=AsyncMock)
    async def test_get_user_groups_empty_list(self, mock_get_groups, mock_get_memberships):
        mock_get_memberships.return_value = []
        result = await GroupService.get_user_groups(ObjectId())
        assert result == []
        mock_get_groups.assert_not_called()
