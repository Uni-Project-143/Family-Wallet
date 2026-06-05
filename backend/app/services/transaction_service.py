import logging
import math
import uuid
from decimal import Decimal

from bson import ObjectId
from bson.errors import InvalidId
from beanie.odm.operators.update.general import Inc

from app.exceptions import (
    DomainException,
    ForbiddenAccessError,
    ResourceNotFoundError,
)
from app.models.bank_card import BankCard
from app.models.category import Category
from app.models.group_membership import GroupMembership
from app.models.transaction import Transaction
from app.repositories.bank_card_repository import BankCardRepository
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction import (
    TransactionFilterParams,
    TransferRequest,
    TransferResponse,
)

logger = logging.getLogger(__name__)


class TransactionService:

    @classmethod
    async def get_transactions(cls, card_ids: list[str], filters: TransactionFilterParams) -> dict:
        items, total_count = await TransactionRepository.get_filtered_transactions(card_ids,
                                                                                   filters)

        total_pages = math.ceil(total_count / filters.size) if total_count > 0 else 1

        return {
            "items": items,
            "total": total_count,
            "page": filters.page,
            "size": filters.size,
            "pages": total_pages
        }

    @classmethod
    async def create_transfer(
        cls,
        payload: TransferRequest,
        current_user_id: str,
    ) -> TransferResponse:
        """
        Створює віртуальний переказ між двома картками однієї сімейної групи.
        Дві immutable Transaction-записи додаються атомарно.
        Raw bank-card balance НЕ мутується — змінюється лише effective_balance.
        """
        # Крок 1 + 2: уніфікований 404 для відсутньої та чужої картки (захист від перебору ID).
        from_card = await BankCardRepository.get_by_id(payload.from_card_id)
        if not from_card or str(from_card.user_id) != str(current_user_id):
            raise ResourceNotFoundError(detail="Картку не знайдено")

        # Крок 3: існування картки-отримувача.
        to_card = await BankCardRepository.get_by_id(payload.to_card_id)
        if not to_card:
            raise ResourceNotFoundError(detail="Картку отримувача не знайдено")

        # Крок 4: обидві картки мають належати одній групі.
        if str(from_card.group_id) != str(to_card.group_id):
            raise DomainException(
                status_code=400,
                detail="Картки належать різним групам",
            )

        # Крок 5: повторна перевірка членства в групі (UC-15 — токен міг пережити вихід з групи).
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
            raise ForbiddenAccessError(
                detail="Доступ заборонено: ви не є учасником цієї групи",
            )

        # Крок 6: обидві картки мають бути ACTIVE.
        if from_card.status != "ACTIVE" or to_card.status != "ACTIVE":
            raise DomainException(status_code=400, detail="Картка деактивована")

        # Крок 7: страховка від переказу на ту саму картку (схема також блокує).
        if str(from_card.id) == str(to_card.id):
            raise DomainException(
                status_code=400,
                detail="Не можна переказувати на ту саму картку",
            )

        # Крок 8: якщо передано категорію — перевіряємо її існування.
        if payload.category_id:
            try:
                category_oid = ObjectId(payload.category_id)
            except (InvalidId, TypeError):
                raise DomainException(
                    status_code=400,
                    detail="Невалідний category_id",
                )
            category = await Category.get(category_oid)
            if not category:
                raise DomainException(
                    status_code=400,
                    detail="Категорію не знайдено",
                )

                # Крок 9: перевірка достатності коштів (використовуємо кешований virtual_balance)
                from_card_id_str = str(from_card.id)
                to_card_id_str = str(to_card.id)
                amount = payload.amount

                if from_card.virtual_balance < amount:
                    raise DomainException(status_code=400, detail="Недостатньо коштів")

                # Крок 10: генеруємо transfer_id для парних транзакцій.
                transfer_id = str(uuid.uuid4())

                # Крок 11: будуємо ноги переказу з нормалізованим знаком (defense-in-depth).
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

                # Крок 12: атомарний парний insert (helper зі Slice 3).
                debit_id, credit_id = await TransactionRepository.create_paired_virtual_transactions(
                    debit, credit,
                )

                # Крок 13: Атомарне оновлення кешованих балансів ($inc)
                # Це захищає нас від Race Condition на рівні бази даних
                await from_card.update(Inc({BankCard.virtual_balance: float(debit_amount)}))
                await to_card.update(Inc({BankCard.virtual_balance: float(credit_amount)}))

                # Крок 14: audit log (security recommendation #4.9).
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

                # Крок 15: повертаємо актуальні кешовані баланси
                return TransferResponse(
                    transfer_id=transfer_id,
                    debit_transaction_id=debit_id,
                    credit_transaction_id=credit_id,
                    amount=amount,
                    from_effective_balance=from_card.virtual_balance - amount,
                    to_effective_balance=to_card.virtual_balance + amount,
                )
