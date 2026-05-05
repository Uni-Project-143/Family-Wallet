from typing import Optional
from bson import ObjectId
from bson.errors import InvalidId
from app.models.bank_card import BankCard

class BankCardRepository:

    @classmethod
    async def get_by_id(cls, card_id: str) -> Optional[BankCard]:
        """Fetches a card by its internal database ID."""
        try:
            return await BankCard.get(ObjectId(card_id))
        except InvalidId:
            return None

    @classmethod
    async def get_by_account_id(cls, account_id: str) -> Optional[BankCard]:
        """Шукає картку за account_id (ідентифікатором рахунку в Monobank)."""
        return await BankCard.find_one(BankCard.account_id == account_id)

    @classmethod
    async def save(cls, card: BankCard) -> BankCard:
        """Зберігає або оновлює картку в базі."""
        await card.save()
        return card

    @classmethod
    async def check_token_exists(cls, token_check: str) -> bool:
         # На цьому етапі ми не можемо просто шукати по токену,
         # тому що він зашифрований з випадковим salt (nonce) кожного разу по-різному.
         # Перевірка на "вже використаний" буде відбуватися пізніше через account_id,
         # який ми отримуємо з Монобанку (він унікальний і постійний).
         pass
