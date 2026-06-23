from fastapi import HTTPException, status
from bson import ObjectId
from app.services.monobank_client import MonobankClient
from app.core.encryption import EncryptionService
from app.models.bank_card import BankCard
from app.repositories.bank_card_repository import BankCardRepository
from app.models.group_membership import GroupMembership
import os
import logging

logger = logging.getLogger(__name__)

class MonobankService:
    @classmethod
    async def connect_card(cls, user_id: str, group_id: str, personal_token: str) -> dict:
        membership = await GroupMembership.find_one(
            GroupMembership.user_id == ObjectId(user_id),
            GroupMembership.group_id == ObjectId(group_id)
        )

        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this group and cannot connect cards."
            )

        client_info = await MonobankClient.get_client_info(personal_token)

        if not client_info.get("accounts"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active accounts found for this token."
            )

        main_account = client_info["accounts"][0]
        account_id = main_account["id"]
        masked_pan = main_account.get("maskedPan", ["•••• Невідомо"])[0]

        existing_card = await BankCardRepository.get_by_account_id(account_id)
        if existing_card:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This account is already connected to the system."
            )

        encrypted_token = EncryptionService.encrypt(personal_token)
        webhook_url = os.getenv("MONOBANK_WEBHOOK_URL")

        if not webhook_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="MONOBANK_WEBHOOK_URL is not configured on the server."
            )

        await MonobankClient.register_webhook(personal_token, webhook_url)

        new_card = BankCard(
            user_id=user_id,
            group_id=group_id,
            encrypted_token=encrypted_token,
            account_id=account_id,
            masked_pan=masked_pan,
            status="ACTIVE"
        )
        await BankCardRepository.save(new_card)

        return {
            "id": str(new_card.id),
            "masked_pan": masked_pan,
            "status": "Active",
            "message": "Card connected successfully"
        }

    @classmethod
    async def disconnect_card(cls, card_id: str, user_id: str) -> dict:
        card = await BankCardRepository.get_by_id(card_id)
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Card not found."
            )

        if card.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only disconnect your own cards."
            )

        try:
            decrypted_token = EncryptionService.decrypt(card.encrypted_token)
            await MonobankClient.register_webhook(decrypted_token, "")
        except Exception as e:
            logger.warning(f"Failed to reset Monobank webhook during disconnect: {e}")

        await BankCardRepository.delete(card)

        return {
            "message": "Card permanently deleted and disconnected successfully."
        }
