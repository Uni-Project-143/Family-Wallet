import asyncio
import sys
import os
from beanie.odm.operators.update.general import Inc

# Знаходимо абсолютний шлях до папки backend
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.config.database import init_db
from app.models.bank_card import BankCard


async def main():
    print("Підключення до бази даних...\n")
    await init_db()

    # Отримуємо всі активні картки
    cards = await BankCard.find({"status": "ACTIVE"}).to_list()

    if not cards:
        print("Активних карток не знайдено.")
        return

    # Виводимо список карток для вибору
    print("Доступні картки:")
    for idx, c in enumerate(cards):
        print(f"[{idx}] Картка: {c.masked_pan} | Поточний баланс: {c.virtual_balance}")
    print("")

    # Даємо користувачу обрати картку
    try:
        choice = int(input("Введіть номер картки зі списку вище (наприклад, 0): "))
        selected_card = cards[choice]
    except (ValueError, IndexError):
        print("Помилка: Невірний номер картки.")
        return

    print(f"\nВибрано: {selected_card.masked_pan}")
    action = input("Введіть '1' щоб ДОДАТИ 5000 грн, або '2' щоб ВІДНЯТИ 5000 грн (відкат): ")

    if action == '1':
        await selected_card.update(Inc({"virtual_balance": float(5000)}))
        print(f"УСПІХ: На картку {selected_card.masked_pan} нараховано 5000 грн.")
    elif action == '2':
        await selected_card.update(Inc({"virtual_balance": float(-5000)}))
        print(f"ВІДКАТ: З картки {selected_card.masked_pan} знято 5000 грн.")
    else:
        print("Невідома дія.")


if __name__ == "__main__":
    asyncio.run(main())
