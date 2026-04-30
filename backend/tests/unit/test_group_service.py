import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta
from bson import ObjectId

from app.services.group_service import GroupService
from app.exceptions import InvalidInviteError, InviteExpiredError

# Допоміжний фейковий токен
class MockInvite:
    def __init__(self, expired=False):
        self.group_id = ObjectId()
        self.token = "valid-token-123"
        self.expires_at = datetime.utcnow() - timedelta(days=1) if expired else datetime.utcnow() + timedelta(days=1)

@pytest.mark.asyncio
class TestGroupService:

    @patch("app.services.group_service.GroupMembership")  # <--- ДОДАЛИ МОК МОДЕЛІ
    @patch("app.services.group_service.InviteRepository.get_by_token")
    @patch("app.services.group_service.GroupRepository.get_membership")
    @patch("app.services.group_service.GroupRepository.add_member")
    @patch("app.services.group_service.InviteRepository.save")
    async def test_join_group_happy_path(self, mock_save, mock_add_member, mock_get_membership,
                                         mock_get_invite, mock_group_membership):
        """Happy Path: Юзер успішно приєднується за валідною лінкою"""
        # Налаштовуємо фейкові відповіді від БД
        mock_get_invite.return_value = MockInvite(expired=False)
        mock_get_membership.return_value = None  # Юзер ще не в групі

        # Викликаємо наш сервіс
        result = await GroupService.join_group("https://family-wallet.com/join/valid-token-123",
                                               ObjectId())

        # Перевіряємо результат
        assert result["message"] == "You have successfully joined the family!"
        mock_add_member.assert_called_once()
        mock_save.assert_called_once()

    @patch("app.services.group_service.InviteRepository.get_by_token")
    async def test_join_group_expired_token(self, mock_get_invite):
        """Negative: Лінка прострочена"""
        mock_get_invite.return_value = MockInvite(expired=True)

        with pytest.raises(InviteExpiredError):
            await GroupService.join_group("https://family-wallet.com/join/valid-token-123", ObjectId())

    @patch("app.services.group_service.InviteRepository.get_by_token")
    async def test_join_group_invalid_format(self, mock_get_invite):
        """Negative: Неправильний формат лінки"""
        with pytest.raises(InvalidInviteError) as exc:
            await GroupService.join_group("just-a-random-string", ObjectId())

        assert "Invalid invite link structure" in str(exc.value.detail)
