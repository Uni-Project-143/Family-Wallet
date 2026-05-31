from app.models.notification import NotificationLog
from app.models.user import User
from app.models.gift_event import GiftEvent
from beanie import PydanticObjectId


class NotificationService:

    @staticmethod
    async def send_notification(user_id: str, gift: GiftEvent, notif_type: str,
                                idempotency_key: str):
        """Відправляє Push/Email, якщо повідомлення з таким ключем ще не відправлялось"""

        # 1. Перевірка Idempotency (BE-03)
        existing = await NotificationLog.find_one({"idempotency_key": idempotency_key})
        if existing:
            return False  # Вже відправляли, ігноруємо

        # 2. Знаходимо юзера, щоб взяти його Email/Token
        try:
            user = await User.get(PydanticObjectId(user_id))
            if not user:
                return False
        except Exception:
            return False

        # 3. Симуляція відправки (Тут буде SendGrid та FCM)
        # TODO: Додати sendgrid.Mail(...) та firebase_admin.messaging(...)
        email_address = getattr(user, 'email', f"user_{user_id}@test.com")
        print(f"[SENDGRID 📧] To: {email_address} | Type: {notif_type} | Gift: {gift.name}")
        print(f"[FCM PUSH 🔔] To User ID: {user_id} | Gift: {gift.name}")

        # 4. Записуємо в лог, щоб не відправити двічі
        log = NotificationLog(
            user_id=user_id,
            gift_id=str(gift.id),
            notification_type=notif_type,
            idempotency_key=idempotency_key
        )
        await log.insert()

        return True
