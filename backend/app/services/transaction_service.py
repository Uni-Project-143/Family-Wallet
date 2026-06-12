import logging
import math
import uuid
from decimal import Decimal
from bson import ObjectId
from bson.errors import InvalidId
from beanie.odm.operators.update.general import Inc
from collections import Counter
from datetime import datetime, timezone

from app.core.websockets import ws_manager
from app.models.transaction import Reaction
from app.exceptions import DomainException, ForbiddenAccessError, ResourceNotFoundError
from app.models.bank_card import BankCard
from app.models.category import Category
from app.models.group_membership import GroupMembership
from app.models.transaction import Transaction
from app.repositories.bank_card_repository import BankCardRepository
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction import TransactionFilterParams, TransferRequest, TransferResponse

logger = logging.getLogger(__name__)

class TransactionService:
    @classmethod
    async def get_transactions(cls, card_ids: list[str], filters: TransactionFilterParams) -> dict:
        items, total_count = await TransactionRepository.get_filtered_transactions(card_ids, filters)
        total_pages = math.ceil(total_count / filters.size) if total_count > 0 else 1

        return {
            "items": items,
            "total": total_count,
            "page": filters.page,
            "size": filters.size,
            "pages": total_pages
        }

    @classmethod
    async def create_transfer(cls, payload: TransferRequest, current_user_id: str) -> TransferResponse:
        from_card = await BankCardRepository.get_by_id(payload.from_card_id)
        if not from_card or str(from_card.user_id) != str(current_user_id):
            raise ResourceNotFoundError(detail="Картку не знайдено")

        to_card = await BankCardRepository.get_by_id(payload.to_card_id)
        if not to_card:
            raise ResourceNotFoundError(detail="Картку отримувача не знайдено")

        if str(from_card.group_id) != str(to_card.group_id):
            raise DomainException(status_code=400, detail="Картки належать різним групам")

        try:
            group_oid = ObjectId(str(from_card.group_id))
            user_oid = ObjectId(str(current_user_id))
        except (InvalidId, TypeError):
            raise ResourceNotFoundError(detail="Картку не знайдено")

        membership = await GroupMembership.find_one({
            "user_id": user_oid,
            "group_id": group_oid,
        })
        if not membership:
            raise ForbiddenAccessError(detail="Доступ заборонено: ви не є учасником цієї групи")

        if from_card.status != "ACTIVE" or to_card.status != "ACTIVE":
            raise DomainException(status_code=400, detail="Картка деактивована")

        if str(from_card.id) == str(to_card.id):
            raise DomainException(status_code=400, detail="Не можна переказувати на ту саму картку")

        if payload.category_id:
            try:
                category_oid = ObjectId(payload.category_id)
            except (InvalidId, TypeError):
                raise DomainException(status_code=400, detail="Невалідний category_id")
            category = await Category.get(category_oid)
            if not category:
                raise DomainException(status_code=400, detail="Категорію не знайдено")

        from_card_id_str = str(from_card.id)
        to_card_id_str = str(to_card.id)
        amount = payload.amount

        if from_card.virtual_balance < amount:
            raise DomainException(status_code=400, detail="Недостатньо коштів")

        transfer_id = str(uuid.uuid4())
        debit_amount = -abs(amount)
        credit_amount = +abs(amount)
        group_id_str = str(from_card.group_id)

        debit = Transaction(
            card_id=from_card_id_str,
            amount=debit_amount,
            currency="UAH",
            category_id=payload.category_id,
            description=payload.description,
            group_id=group_id_str,
            is_virtual=True,
            transfer_id=transfer_id,
        )
        credit = Transaction(
            card_id=to_card_id_str,
            amount=credit_amount,
            currency="UAH",
            category_id=payload.category_id,
            description=payload.description,
            group_id=group_id_str,
            is_virtual=True,
            transfer_id=transfer_id,
        )

        debit_id, credit_id = await TransactionRepository.create_paired_virtual_transactions(debit, credit)

        await from_card.update(Inc({BankCard.virtual_balance: float(debit_amount)}))
        await to_card.update(Inc({BankCard.virtual_balance: float(credit_amount)}))

        logger.info(
            "VIRTUAL_TRANSFER",
            extra={
                "user_id": str(current_user_id),
                "transfer_id": transfer_id,
                "from_card_id": from_card_id_str,
                "to_card_id": to_card_id_str,
                "amount": str(amount),
            },
        )

        # Крок 15: real-time push у стрічку групи — щоб переказ зʼявився
        # у всіх учасників без перезавантаження (фронт робить рефетч /feed).
        await ws_manager.broadcast_to_group(
            group_id_str,
            {
                "event": "new_transaction",
                "data": {
                    "transfer_id": transfer_id,
                    "from_card_id": from_card_id_str,
                    "to_card_id": to_card_id_str,
                    "amount": str(amount),
                    "group_id": group_id_str,
                },
            },
        )

        # Крок 16: повертаємо актуальні кешовані баланси
        return TransferResponse(
            transfer_id=transfer_id,
            debit_transaction_id=debit_id,
            credit_transaction_id=credit_id,
            amount=amount,
            from_effective_balance=from_card.virtual_balance - amount,
            to_effective_balance=to_card.virtual_balance + amount,
        )

    @classmethod
    async def react_to_transaction(cls, transaction_id: str, user_id: str, emoji: str) -> dict:
        try:
            tx_oid = ObjectId(transaction_id)
        except (InvalidId, TypeError):
            raise ResourceNotFoundError(detail="Невірний формат ID транзакції")

        transaction = await Transaction.get(tx_oid)
        if not transaction:
            raise ResourceNotFoundError(detail="Транзакцію не знайдено")

        membership = await GroupMembership.find_one({
            "user_id": ObjectId(user_id),
            "group_id": ObjectId(transaction.group_id)
        })
        if not membership:
            raise ForbiddenAccessError(detail="Ви не можете реагувати на транзакції іншої групи")

        existing_reaction_idx = next(
            (i for i, r in enumerate(transaction.reactions) if str(r.user_id) == str(user_id)),
            None
        )

        if existing_reaction_idx is not None:
            if transaction.reactions[existing_reaction_idx].emoji == emoji:
                transaction.reactions.pop(existing_reaction_idx)
            else:
                transaction.reactions[existing_reaction_idx].emoji = emoji
                transaction.reactions[existing_reaction_idx].created_at = datetime.now(timezone.utc)
        else:
            new_reaction = Reaction(user_id=user_id, emoji=emoji)
            transaction.reactions.append(new_reaction)

        await transaction.save()

        total_count = len(transaction.reactions)
        grouped_reactions = dict(Counter(r.emoji for r in transaction.reactions))

        ws_payload = {
            "event": "reaction_updated",
            "data": {
                "transaction_id": transaction_id,
                "user_id": user_id,
                "emoji": emoji,
                "total_count": total_count,
                "grouped_reactions": grouped_reactions
            }
        }

        await ws_manager.broadcast_to_group(str(transaction.group_id), ws_payload)

        return {
            "status": "success",
            "total_count": total_count,
            "grouped_reactions": grouped_reactions
        }
