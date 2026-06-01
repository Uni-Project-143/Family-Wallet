from app.models.transaction import Transaction
from app.schemas.transaction import TransactionFilterParams, TransactionType
from datetime import datetime, time


class TransactionRepository:

    @staticmethod
    async def get_filtered_transactions(card_ids: list[str], filters: TransactionFilterParams):
        # 1. Завжди шукаємо тільки по картках поточного юзера
        query = {"card_id": {"$in": card_ids}}

        # 2. Фільтр по категорії
        if filters.category_id:
            query["category_id"] = filters.category_id

        # 3. Фільтр по типу та сумі
        amount_query = {}
        if filters.tx_type == TransactionType.INCOME:
            amount_query["$gt"] = 0
            if filters.min_amount is not None: amount_query["$gte"] = filters.min_amount
            if filters.max_amount is not None: amount_query["$lte"] = filters.max_amount

        elif filters.tx_type == TransactionType.EXPENSE:
            amount_query["$lt"] = 0
            # Оскільки витрати негативні (-500), логіка перевертається
            if filters.min_amount is not None: amount_query["$lte"] = -filters.min_amount
            if filters.max_amount is not None: amount_query["$gte"] = -filters.max_amount
        else:
            # Якщо тип не вибрано, шукаємо просто додатні числа (щоб не ламати логіку)
            if filters.min_amount is not None: amount_query["$gte"] = filters.min_amount
            if filters.max_amount is not None: amount_query["$lte"] = filters.max_amount

        if amount_query:
            query["amount"] = amount_query

        # 4. Фільтр по датах (обробка кінця дня)
        if filters.start_date or filters.end_date:
            query["timestamp"] = {}
            if filters.start_date:
                query["timestamp"]["$gte"] = datetime.combine(filters.start_date, time.min)
            if filters.end_date:
                query["timestamp"]["$lte"] = datetime.combine(filters.end_date, time.max)

        # 5. Пагінація та сортування
        sort_dir = -1 if filters.sort_order == "desc" else 1
        skip = (filters.page - 1) * filters.size

        # 6. Запити до бази
        total_count = await Transaction.find(query).count()
        docs = await Transaction.find(query).sort((filters.sort_by.value, sort_dir)).skip(
            skip).limit(filters.size).to_list()

        # 7. Конвертація в словники для Pydantic
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
                "is_virtual": getattr(doc, "is_virtual", False),
                "transfer_id": getattr(doc, "transfer_id", None),
            })

        return transactions, total_count
