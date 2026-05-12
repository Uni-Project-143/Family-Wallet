from app.schemas.transaction import TransactionFilterParams
from app.repositories.transaction_repository import TransactionRepository
import math


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
