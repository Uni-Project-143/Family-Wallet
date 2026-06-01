from decimal import Decimal
from typing import Optional
from bson import ObjectId
from bson.decimal128 import Decimal128
from bson.errors import InvalidId
from app.models.bank_card import BankCard
from app.models.transaction import Transaction

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

    @classmethod
    async def get_virtual_deltas_by_card_ids(cls, card_ids: list[str]) -> dict[str, Decimal]:
        """
        Computes sum of is_virtual=True transaction amounts per card, in a single aggregation.
        Returns {card_id: delta} mapping. Cards with no virtual tx are NOT in the result
        — callers should default to Decimal("0").
        """
        if not card_ids:
            return {}

        pipeline = [
            {"$match": {"card_id": {"$in": card_ids}, "is_virtual": True}},
            {"$group": {"_id": "$card_id", "delta": {"$sum": "$amount"}}},
        ]

        cursor = Transaction.get_motor_collection().aggregate(pipeline)
        result: dict[str, Decimal] = {}
        async for doc in cursor:
            raw_delta = doc["delta"]
            if isinstance(raw_delta, Decimal128):
                delta = raw_delta.to_decimal()
            else:
                delta = Decimal(str(raw_delta))
            result[doc["_id"]] = delta
        return result
