from fastapi import HTTPException, status
from bson import ObjectId
from app.services.monobank_client import MonobankClient
from app.core.encryption import EncryptionService
from app.models.bank_card import BankCard
from app.repositories.bank_card_repository import BankCardRepository
from app.models.group_membership import GroupMembership

class MonobankService:

    @classmethod
    async def connect_card(cls, user_id: str, group_id: str, personal_token: str) -> dict:
        """
        Головний метод підключення картки.
        Відповідає всім AC з таски.
        """
        membership = await GroupMembership.find_one(
            GroupMembership.user_id == ObjectId(user_id),
            GroupMembership.group_id == ObjectId(group_id)
        )

        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this group and cannot connect cards."
            )

        # 2. BE-01: Валідація токена через MonobankClient
        client_info = await MonobankClient.get_client_info(personal_token)

        # Беремо перший рахунок (або можна дати юзеру вибір, але поки беремо перший активний)
        # У реальності Монобанк повертає список `accounts`
        if not client_info.get("accounts"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active accounts found for this token."
            )

        main_account = client_info["accounts"][0]
        account_id = main_account["id"]
        masked_pan = main_account.get("maskedPan", ["•••• Невідомо"])[0]

        # 3. Negative AC: Перевірка, чи картка вже підключена
        existing_card = await BankCardRepository.get_by_account_id(account_id)
        if existing_card:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This account is already connected to the system."
            )

        # 4. BE-03: Шифрування токена
        encrypted_token = EncryptionService.encrypt(personal_token)

        # 5. BE-02: Реєстрація webhook у Monobank
        # ВАЖЛИВО: Твій сервер має бути доступний з інтернету (ngrok/vps),
        # щоб Монобанк міг слати сюди вебхуки.
        # Поки що ставимо заглушку або твій реальний URL, якщо він є.
        # Наприклад: "webhook_url = "https://overblown-whoopee-labored.ngrok-free.dev/api/v1/monobank/webhook"
        webhook_url = "https://overblown-whoopee-labored.ngrok-free.dev/api/v1/monobank/webhook"

        # РОЗКОМЕНТУЙ цю лінію, коли матимеш публічну адресу (ngrok), інакше Монобанк відхилить запит
        await MonobankClient.register_webhook(personal_token, webhook_url)

        # 6. Збереження в базу (DB-01)
        new_card = BankCard(
            user_id=user_id,
            group_id=group_id,
            encrypted_token=encrypted_token,
            account_id=account_id,
            masked_pan=masked_pan,
            status="ACTIVE"
        )
        await BankCardRepository.save(new_card)

        # 7. Позитивний AC: Повертаємо дані для UI
        return {
            "masked_pan": masked_pan,
            "status": "Active",
            "message": "Card connected successfully"
        }

    @classmethod
    async def disconnect_card(cls, card_id: str, user_id: str) -> dict:
        """
        Disconnects the card and completely removes it from the database (Hard delete).
        """
        # 1. Шукаємо картку
        card = await BankCardRepository.get_by_id(card_id)
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Card not found."
            )

        # 2. Перевірка власності картки
        if card.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only disconnect your own cards."
            )

        # (Прибрали перевірку на INACTIVE, бо ми тепер видаляємо фізично)

        # 3. Скидання webhook у Monobank API
        try:
            decrypted_token = EncryptionService.decrypt(card.encrypted_token)
            await MonobankClient.register_webhook(decrypted_token, "")
        except Exception as e:
            print(f"Warning: Failed to reset Monobank webhook: {e}")

        # 4. HARD DELETE: Фізично видаляємо картку з БД
        await BankCardRepository.delete(card)

        # 5. Успішна відповідь (текст трішки змінили для відображення реальності)
        return {
            "message": "Card permanently deleted and disconnected successfully."
        }
