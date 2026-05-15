import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException
from bson import ObjectId

from app.services.monobank_service import MonobankService


@pytest.mark.asyncio
class TestMonobankServiceUnit:

    @patch("app.services.monobank_service.BankCard")  # ГЛУШИМО BEANIE
    @patch("app.services.monobank_service.GroupMembership")  # ГЛУШИМО BEANIE
    @patch("app.services.monobank_service.MonobankClient.get_client_info", new_callable=AsyncMock)
    @patch("app.services.monobank_service.BankCardRepository.get_by_account_id",
           new_callable=AsyncMock)
    @patch("app.services.monobank_service.EncryptionService.encrypt")
    @patch("app.services.monobank_service.MonobankClient.register_webhook", new_callable=AsyncMock)
    @patch("app.services.monobank_service.BankCardRepository.save", new_callable=AsyncMock)
    async def test_connect_card_happy_path(
        self, mock_save, mock_webhook, mock_encrypt, mock_get_card, mock_get_info,
        mock_membership_class, mock_bankcard_class
    ):
        # Налаштовуємо асинхронний метод find_one всередині нашого класу-манекена
        mock_membership_class.find_one = AsyncMock(return_value=MagicMock())

        mock_get_info.return_value = {"accounts": [{"id": "acc123", "maskedPan": ["1234"]}]}
        mock_get_card.return_value = None
        mock_encrypt.return_value = "encrypted_token"
        mock_webhook.return_value = True

        valid_user_id = str(ObjectId())
        valid_group_id = str(ObjectId())

        result = await MonobankService.connect_card(valid_user_id, valid_group_id, "real_token")

        assert result["status"] == "Active"
        assert result["masked_pan"] == "1234"
        mock_save.assert_called_once()
        mock_webhook.assert_called_once()

    @patch("app.services.monobank_service.GroupMembership")  # ГЛУШИМО BEANIE
    async def test_connect_card_not_a_member_403(self, mock_membership_class):
        mock_membership_class.find_one = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc:
            await MonobankService.connect_card(str(ObjectId()), str(ObjectId()), "token")

        assert exc.value.status_code == 403

    @patch("app.services.monobank_service.GroupMembership")  # ГЛУШИМО BEANIE
    @patch("app.services.monobank_service.MonobankClient.get_client_info", new_callable=AsyncMock)
    async def test_connect_card_no_accounts_400(self, mock_get_info, mock_membership_class):
        mock_membership_class.find_one = AsyncMock(return_value=MagicMock())
        mock_get_info.return_value = {"accounts": []}

        with pytest.raises(HTTPException) as exc:
            await MonobankService.connect_card(str(ObjectId()), str(ObjectId()), "token")

        assert exc.value.status_code == 400

    @patch("app.services.monobank_service.GroupMembership")  # ГЛУШИМО BEANIE
    @patch("app.services.monobank_service.MonobankClient.get_client_info", new_callable=AsyncMock)
    @patch("app.services.monobank_service.BankCardRepository.get_by_account_id",
           new_callable=AsyncMock)
    async def test_connect_card_already_exists_409(self, mock_get_card, mock_get_info,
                                                   mock_membership_class):
        mock_membership_class.find_one = AsyncMock(return_value=MagicMock())
        mock_get_info.return_value = {"accounts": [{"id": "acc123", "maskedPan": ["1234"]}]}
        mock_get_card.return_value = MagicMock()  # Картка вже є

        with pytest.raises(HTTPException) as exc:
            await MonobankService.connect_card(str(ObjectId()), str(ObjectId()), "token")

        assert exc.value.status_code == 409
