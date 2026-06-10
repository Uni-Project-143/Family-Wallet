import asyncio
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from beanie.odm.operators.update.general import Inc

from app.models.gift_event import GiftEvent, GiftStatus
from app.models.group_membership import GroupMembership
from app.models.bank_card import BankCard
from app.models.transaction import Transaction
from app.services.notification_service import NotificationService


class GiftService:

    @staticmethod
    async def reveal_gifts_cron():
        """Cron Job: перевіряє дати розкриття та нагадування"""
        try:
            while True:
                try:
                    now = datetime.now(timezone.utc).replace(tzinfo=None)

                    active_gifts = await GiftEvent.find(
                        GiftEvent.status == GiftStatus.ACTIVE
                    ).to_list()

                    if active_gifts:
                        print(
                            f"[CRON] now(UTC)={now:%Y-%m-%d %H:%M:%S} | активних подій: {len(active_gifts)}")

                    for gift in active_gifts:
                        gift_id_str = str(gift.id)

                        unlock_date_naive = gift.unlock_date.replace(tzinfo=None)
                        seconds_left = (unlock_date_naive - now).total_seconds()
                        print(
                            f"[CRON]   '{gift.name}' unlock(UTC)={unlock_date_naive:%Y-%m-%d %H:%M:%S} "
                            f"| залишилось {int(seconds_left)} с"
                        )

                        # 1. РОЗКРИТТЯ ПОДАРУНКА
                        if unlock_date_naive <= now:
                            gift.status = GiftStatus.REVEALED
                            await gift.save()
                            print(f"[CRON] 🎁 Подарунок '{gift.name}' РОЗКРИТО (unlock минув)!")

                            # Підрахунок зібраних коштів та зарахування
                            gift_txs = await Transaction.find(
                                Transaction.gift_id == str(gift.id)).to_list()
                            total_collected = sum(abs(tx.amount) for tx in gift_txs)

                            if total_collected > 0:
                                target_card = await BankCard.find_one(
                                    BankCard.user_id == gift.target_user_id,
                                    BankCard.group_id == gift.group_id,
                                    BankCard.status == "ACTIVE"
                                )
                                if target_card:
                                    # Атомарне зарахування всієї зібраної суми імениннику
                                    await target_card.update(
                                        Inc({BankCard.virtual_balance: float(total_collected)}))

                                    # Транзакція поповнення для стрічки
                                    payout_tx = Transaction(
                                        card_id=str(target_card.id),
                                        amount=Decimal(str(total_collected)),
                                        currency="UAH",
                                        group_id=gift.group_id,
                                        category_id="gift_payout",
                                        description=f"🎁 Отримано Secret Gift: {gift.name}",
                                        is_virtual=True,
                                        is_secret_gift=True,
                                        gift_id=str(gift.id)
                                    )
                                    await payout_tx.insert()
                                    print(
                                        f"[CRON] 💰 Кошти ({total_collected}) успішно зараховано імениннику!")
                                else:
                                    print(
                                        f"[CRON ERROR] В іменинника немає активної картки для зарахування!")

                            await NotificationService.send_notification(
                                user_id=gift.target_user_id,
                                gift=gift,
                                notif_type="REVEAL",
                                idempotency_key=f"{gift_id_str}_reveal"
                            )
                            continue

                        # 2. НАГАДУВАННЯ ЗА 24 ГОДИНИ
                        time_until_unlock = unlock_date_naive - now
                        if timedelta(hours=23, minutes=58) <= time_until_unlock <= timedelta(
                            hours=24, minutes=2):
                            await GiftService._notify_group_except_target(
                                gift, "REMINDER_24H", f"{gift_id_str}_remind_24h"
                            )

                        # 3. НАГАДУВАННЯ В ДЕНЬ РОЗКРИТТЯ
                        if timedelta(hours=0) < time_until_unlock <= timedelta(hours=10):
                            if now.date() == unlock_date_naive.date():
                                await GiftService._notify_group_except_target(
                                    gift, "REMINDER_DAY_OF", f"{gift_id_str}_remind_day_of"
                                )

                except Exception as e:
                    print(f"[CRON ERROR] Помилка виконання: {e}")

                await asyncio.sleep(30)

        except asyncio.CancelledError:
            print("[CRON] Роботу фонової задачі коректно завершено.")

    @staticmethod
    async def _notify_group_except_target(gift: GiftEvent, notif_type: str,
                                          idempotency_key_prefix: str):
        memberships = await GroupMembership.find(
            GroupMembership.group_id == getattr(gift, 'group_id', None)
        ).to_list()

        for m in memberships:
            member_id = str(m.user_id)
            if member_id != gift.target_user_id:
                user_idemp_key = f"{idempotency_key_prefix}_{member_id}"
                await NotificationService.send_notification(
                    user_id=member_id,
                    gift=gift,
                    notif_type=notif_type,
                    idempotency_key=user_idemp_key
                )
