import asyncio
from datetime import datetime, timezone, timedelta
from app.models.gift_event import GiftEvent, GiftStatus
from app.models.group_membership import GroupMembership
from app.services.notification_service import NotificationService


class GiftService:

    @staticmethod
    async def reveal_gifts_cron():
        """Cron Job: перевіряє дати розкриття та нагадування"""
        try:
            while True:
                try:
                    # 1. Робимо поточний час "наївним", відрізаючи таймзону
                    now = datetime.now(timezone.utc).replace(tzinfo=None)

                    # Шукаємо всі активні подарунки
                    active_gifts = await GiftEvent.find(
                        GiftEvent.status == GiftStatus.ACTIVE
                    ).to_list()

                    for gift in active_gifts:
                        gift_id_str = str(gift.id)

                        # 2. Робимо час з бази також "наївним" перед будь-якими порівняннями
                        unlock_date_naive = gift.unlock_date.replace(tzinfo=None)

                        # 1. РОЗКРИТТЯ ПОДАРУНКА (PROJ-64 BE-01)
                        if unlock_date_naive <= now:
                            gift.status = GiftStatus.REVEALED
                            await gift.save()
                            print(f"[CRON] Подарунок {gift.name} успішно розкрито!")

                            # Надсилаємо імениннику
                            await NotificationService.send_notification(
                                user_id=gift.target_user_id,
                                gift=gift,
                                notif_type="REVEAL",
                                idempotency_key=f"{gift_id_str}_reveal"
                            )
                            continue  # Ідемо до наступного подарунка

                        # 2. НАГАДУВАННЯ ЗА 24 ГОДИНИ (BE-01)
                        time_until_unlock = unlock_date_naive - now
                        if timedelta(hours=23, minutes=58) <= time_until_unlock <= timedelta(hours=24, minutes=2):
                            await GiftService._notify_group_except_target(
                                gift, "REMINDER_24H", f"{gift_id_str}_remind_24h"
                            )

                        # 3. НАГАДУВАННЯ В ДЕНЬ РОЗКРИТТЯ (BE-02)
                        # Якщо до розкриття менше 10 годин і це той самий день
                        if timedelta(hours=0) < time_until_unlock <= timedelta(hours=10):
                            if now.date() == unlock_date_naive.date():
                                await GiftService._notify_group_except_target(
                                    gift, "REMINDER_DAY_OF", f"{gift_id_str}_remind_day_of"
                                )

                except Exception as e:
                    print(f"[CRON ERROR] Помилка виконання: {e}")

                await asyncio.sleep(60)

        except asyncio.CancelledError:
            print("[CRON] Роботу фонової задачі коректно завершено.")

    @staticmethod
    async def _notify_group_except_target(gift: GiftEvent, notif_type: str,
                                          idempotency_key_prefix: str):
        """Допоміжний метод для надсилання листів учасникам збору (крім іменинника)"""
        memberships = await GroupMembership.find(
            GroupMembership.group_id == getattr(gift, 'group_id', None)
        ).to_list()

        for m in memberships:
            member_id = str(m.user_id)
            if member_id != gift.target_user_id:
                # Унікальний ключ для кожного юзера в рамках одного нагадування
                user_idemp_key = f"{idempotency_key_prefix}_{member_id}"
                await NotificationService.send_notification(
                    user_id=member_id,
                    gift=gift,
                    notif_type=notif_type,
                    idempotency_key=user_idemp_key
                )
