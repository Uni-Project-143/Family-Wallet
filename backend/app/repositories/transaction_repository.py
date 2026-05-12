from app.models.transaction import Transaction  # Підстав свій імпорт моделі
from app.schemas.transaction import TransactionFilterParams
from pymongo import DESCENDING, ASCENDING


class TransactionRepository:

    @staticmethod
    async def get_filtered_transactions(group_id: str, filters: TransactionFilterParams):
        # 1. Базовий запит: юзер бачить тільки транзакції своєї групи/сім'ї
        query = {"group_id": group_id}

        # 2. Динамічно додаємо фільтри, якщо фронтенд їх передав
        if filters.category:
            query["category"] = filters.category

        if filters.tx_type:
            query["type"] = filters.tx_type.value

        # Фільтр по сумі (від і до)
        if filters.min_amount is not None or filters.max_amount is not None:
            query["amount"] = {}
            if filters.min_amount is not None:
                query["amount"]["$gte"] = filters.min_amount
            if filters.max_amount is not None:
                query["amount"]["$lte"] = filters.max_amount

        # Фільтр по даті
        if filters.start_date or filters.end_date:
            query["time"] = {}
            if filters.start_date:
                query["time"]["$gte"] = filters.start_date
            if filters.end_date:
                query["time"]["$lte"] = filters.end_date

        # 3. Налаштування сортування
        direction = DESCENDING if filters.sort_order == "desc" else ASCENDING
        sort_query = [(filters.sort_by.value, direction)]

        # 4. Налаштування пагінації
        skip = (filters.page - 1) * filters.size

        # 5. Виконання запиту до MongoDB (Beanie)
        total_count = await Transaction.find(query).count()
        transactions = await Transaction.find(query).sort(sort_query).skip(skip).limit(
            filters.size).to_list()

        return transactions, total_count
