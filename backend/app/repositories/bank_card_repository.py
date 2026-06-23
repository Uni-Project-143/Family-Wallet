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
        try:
            return await BankCard.get(ObjectId(card_id))
        except InvalidId:
            return None

    @classmethod
    async def get_by_account_id(cls, account_id: str) -> Optional[BankCard]:
        return await BankCard.find_one(BankCard.account_id == account_id)

    @classmethod
    async def save(cls, card: BankCard) -> BankCard:
        await card.save()
        return card

    @classmethod
    async def delete(cls, card: BankCard) -> None:
        await card.delete()

    @classmethod
    async def get_virtual_deltas_by_card_ids(cls, card_ids: list[str]) -> dict[str, Decimal]:
        if not card_ids:
            return {}

        pipeline = [
            {"$match": {"card_id": {"$in": card_ids}, "is_virtual": True}},
            {"$group": {"_id": "$card_id", "delta": {"$sum": "$amount"}}},
        ]

        collection = Transaction.get_pymongo_collection()
        cursor = collection.aggregate(pipeline)
        docs = await cursor.to_list(length=None)

        result: dict[str, Decimal] = {}
        for doc in docs:
            raw_delta = doc["delta"]
            if isinstance(raw_delta, Decimal128):
                delta = raw_delta.to_decimal()
            else:
                delta = Decimal(str(raw_delta))
            result[doc["_id"]] = delta

        return result
