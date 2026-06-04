import os
import firebase_admin
from firebase_admin import credentials, messaging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.models.notification import NotificationLog
from app.models.user import User
from app.models.gift_event import GiftEvent
from beanie import PydanticObjectId

# Ініціалізація Firebase (виконується один раз при старті сервера)
if not firebase_admin._apps:
    try:
        # Шлях до файлу ключів Firebase береться зі змінних середовища
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-adminsdk.json")
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            print(
                "[FIREBASE WARNING] Файл ключів Firebase не знайдено. Push-сповіщення будуть вимкнені.")
    except Exception as e:
        print(f"[FIREBASE ERROR] Не вдалося ініціалізувати Firebase: {e}")


class NotificationService:

    @staticmethod
    async def send_notification(user_id: str, gift: GiftEvent, notif_type: str,
                                idempotency_key: str):
        """Відправляє Push та Email, жорстко контролюючи idempotency_key"""

        # 1. Перевірка Idempotency (Захист від дублів)
        existing = await NotificationLog.find_one({"idempotency_key": idempotency_key})
        if existing:
            return False

            # 2. Отримуємо дані юзера
        try:
            user = await User.get(PydanticObjectId(user_id))
            if not user:
                return False
        except Exception:
            return False

        # Формуємо тексти
        subject, body, push_title, push_body = NotificationService._get_notification_content(
            notif_type, gift)

        # 3. Бойова відправка Email через SendGrid
        email = getattr(user, 'email', None)
        print(f"[NOTIFY] {notif_type}: одержувач user={user_id}, email={email}")
        if email:
            await NotificationService._send_email_sendgrid(email, subject, body)
        else:
            print(f"[NOTIFY] ⚠️ У користувача {user_id} немає email — лист не надіслано.")

        # 4. Бойова відправка Push через FCM
        # Передбачаємо, що фронтенд передає і ми зберігаємо fcm_token у моделі User
        fcm_token = getattr(user, 'fcm_token', None)
        if fcm_token:
            await NotificationService._send_push_fcm(fcm_token, push_title, push_body)

        # 5. Запис у лог (фіксація Idempotency)
        log = NotificationLog(
            user_id=user_id,
            gift_id=str(gift.id),
            notification_type=notif_type,
            idempotency_key=idempotency_key
        )
        await log.insert()

        return True

    @staticmethod
    def _get_notification_content(notif_type: str, gift: GiftEvent):
        """Генератор контенту для листів та пушів"""
        if notif_type == "REVEAL":
            subject = f"🎁 Сюрприз! Подарунок '{gift.name}' розкрито!"
            body = f"<strong>Вітаємо!</strong><br>Збір на подарунок '{gift.name}' завершено та розкрито. Зайдіть у додаток, щоб побачити деталі та привітання!"
            push_title = "Подарунок розкрито! 🎉"
            push_body = f"Зайдіть, щоб побачити хто скинувся на '{gift.name}'"

        elif notif_type == "REMINDER_24H":
            subject = f"⏳ Нагадування: 24 години до розкриття '{gift.name}'"
            body = f"Привіт!<br>Нагадуємо, що завтра розкриття сюрпризу '{gift.name}'. Встигніть зробити свій внесок!"
            push_title = "Залишилось 24 години ⏰"
            push_body = f"Сюрприз '{gift.name}' скоро буде розкрито. Встигніть долучитись!"

        elif notif_type == "REMINDER_DAY_OF":
            subject = f"🔥 Сьогодні розкриваємо подарунок '{gift.name}'!"
            body = f"Привіт!<br>Вже сьогодні ми даруємо '{gift.name}'. Це останній шанс зробити свій секретний внесок!"
            push_title = "Сьогодні свято! 🥳"
            push_body = f"Розкриваємо '{gift.name}'. Останній шанс долучитися!"

        else:
            subject = f"Оновлення події '{gift.name}'"
            body = f"Перевірте додаток для деталей про подію '{gift.name}'."
            push_title = "Оновлення події"
            push_body = f"Новини щодо '{gift.name}'"

        return subject, body, push_title, push_body

    @staticmethod
    async def _send_email_sendgrid(to_email: str, subject: str, html_content: str):
        """API-виклик до SendGrid"""
        sg_api_key = os.getenv("SENDGRID_API_KEY")
        from_email = os.getenv("SENDGRID_FROM_EMAIL", "noreply@family-wallet.com")

        if not sg_api_key:
            print(
                f"[SENDGRID] Пропущено (немає SENDGRID_API_KEY). Лист для {to_email} не відправлено.")
            return

        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        try:
            sg = SendGridAPIClient(sg_api_key)
            response = sg.send(message)
            print(
                f"[SENDGRID] Лист успішно відправлено на {to_email} (Status: {response.status_code})")
        except Exception as e:
            print(f"[SENDGRID ERROR] Помилка відправки: {e}")

    @staticmethod
    async def _send_push_fcm(token: str, title: str, body: str):
        """API-виклик до Firebase Cloud Messaging"""
        if not firebase_admin._apps:
            return

        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=token,
        )
        try:
            response = messaging.send(message)
            print(f"[FCM] Пуш успішно відправлено. ID: {response}")
        except Exception as e:
            print(f"[FCM ERROR] Помилка відправки пуша: {e}")
