import logging
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionFilterParams, TransactionType
from app.config.database import db_client
from datetime import datetime, time

logger = logging.getLogger(__name__)

class TransactionRepository:
    @staticmethod
    async def get_filtered_transactions(card_ids: list[str], filters: TransactionFilterParams):
        query = {"card_id": {"$in": card_ids}}

        if filters.category_id:
            query["category_id"] = filters.category_id

        amount_query = {}
        if filters.tx_type == TransactionType.INCOME:
            amount_query["$gt"] = 0
            if filters.min_amount is not None: amount_query["$gte"] = filters.min_amount
            if filters.max_amount is not None: amount_query["$lte"] = filters.max_amount

        elif filters.tx_type == TransactionType.EXPENSE:
            amount_query["$lt"] = 0
            if filters.min_amount is not None: amount_query["$lte"] = -filters.min_amount
            if filters.max_amount is not None: amount_query["$gte"] = -filters.max_amount
        else:
            if filters.min_amount is not None: amount_query["$gte"] = filters.min_amount
            if filters.max_amount is not None: amount_query["$lte"] = filters.max_amount

        if amount_query:
            query["amount"] = amount_query

        if filters.start_date or filters.end_date:
            query["timestamp"] = {}
            if filters.start_date:
                query["timestamp"]["$gte"] = datetime.combine(filters.start_date, time.min)
            if filters.end_date:
                query["timestamp"]["$lte"] = datetime.combine(filters.end_date, time.max)

        sort_dir = -1 if filters.sort_order == "desc" else 1
        skip = (filters.page - 1) * filters.size

        total_count = await Transaction.find(query).count()
        docs = await Transaction.find(query).sort((filters.sort_by.value, sort_dir)).skip(skip).limit(filters.size).to_list()

        transactions = []
        for doc in docs:
            transactions.append({
                "id": str(doc.id),
                "card_id": doc.card_id,
                "amount": doc.amount,
                "currency": doc.currency,
                "category_id": doc.category_id,
                "description": doc.description,
                "timestamp": doc.timestamp,
                "reactions": doc.reactions,
                "is_virtual": doc.is_virtual,
                "transfer_id": doc.transfer_id,
            })

        return transactions, total_count

    @staticmethod
    async def create_paired_virtual_transactions(
        debit: Transaction,
        credit: Transaction,
    ) -> tuple[str, str]:
        async with await db_client.start_session() as session:
            async with session.start_transaction():
                try:
                    await debit.insert(session=session)
                    await credit.insert(session=session)
                except Exception as exc:
                    logger.critical(
                        "TRANSFER_ROLLBACK_FAILED",
                        extra={
                            "transfer_id": debit.transfer_id,
                            "debit_card_id": debit.card_id,
                            "credit_card_id": credit.card_id,
                            "amount": str(debit.amount),
                            "error": str(exc),
                        },
                    )
                    raise
        return str(debit.id), str(credit.id)
