import asyncio
from datetime import datetime, timezone
from app.models.gift_event import GiftEvent, GiftStatus


class GiftService:

    @staticmethod
    async def reveal_gifts_cron():
        """Фонова задача (Cron), що кожні 60 сек перевіряє UnlockDate"""
        try:
            while True:
                try:
                    now = datetime.now(timezone.utc)
                    gifts_to_reveal = await GiftEvent.find(
                        GiftEvent.status == GiftStatus.ACTIVE,
                        GiftEvent.unlock_date <= now
                    ).to_list()

                    for gift in gifts_to_reveal:
                        gift.status = GiftStatus.REVEALED
                        await gift.save()
                        print(f"[CRON] Подарунок {gift.name} (ID: {gift.id}) успішно розкрито!")

                except Exception as e:
                    print(f"[CRON ERROR] Помилка виконання: {e}")

                # Чекаємо 60 секунд до наступної перевірки
                await asyncio.sleep(60)

        # Цей блок ловить сигнал вимкнення сервера
        except asyncio.CancelledError:
            print("[CRON] Роботу фонової задачі коректно завершено.")

