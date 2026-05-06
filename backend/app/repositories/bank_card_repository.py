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
    async def delete(cls, card: BankCard) -> None:
        """Повне видалення картки з бази (Hard Delete)."""
        await card.delete()
