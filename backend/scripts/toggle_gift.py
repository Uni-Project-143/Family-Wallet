import asyncio
import sys
import os

# Знаходимо абсолютний шлях до папки backend
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.config.database import init_db
from app.models.gift_event import GiftEvent, GiftStatus


async def main():
    print("Підключення до бази даних...\n")
    await init_db()

    # Шукаємо ВСІ активні подарунки
    active_gifts = await GiftEvent.find(GiftEvent.status == GiftStatus.ACTIVE).to_list()

    if active_gifts:
        # ВНОСИМО ЗМІНУ: Розкриваємо всі знайдені подарунки
        for gift in active_gifts:
            gift.status = GiftStatus.REVEALED
            await gift.save()
            print(f"УСПІХ: Подарунок '{gift.name}' примусово РОЗКРИТО (REVEALED)!")
    else:
        # ВІДКАТ (Rollback): Шукаємо ВСІ розкриті і повертаємо назад
        revealed_gifts = await GiftEvent.find(GiftEvent.status == GiftStatus.REVEALED).to_list()

        if revealed_gifts:
            for gift in revealed_gifts:
                gift.status = GiftStatus.ACTIVE
                await gift.save()
                print(f"⏪ ВІДКАТ: Подарунок '{gift.name}' знову ПРИХОВАНО (ACTIVE)!")
        else:
            print("Не знайдено жодного подарунка для зміни.")


if __name__ == "__main__":
    asyncio.run(main())
