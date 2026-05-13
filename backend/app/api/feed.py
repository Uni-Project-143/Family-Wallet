from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.auth import get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from app.models.bank_card import BankCard
from app.models.group_membership import GroupMembership
from app.schemas.feed import FeedResponse, FeedTransactionItem
from beanie import PydanticObjectId

router = APIRouter(prefix="/api/v1/feed", tags=["Feed"])


@router.get("/{group_id}", response_model=FeedResponse)
async def get_unified_feed(
    group_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    # 1. КОНВЕРТУЄМО group_id з рядка в ObjectId
    try:
        group_oid = PydanticObjectId(group_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Невалідний ID групи")

    # 2. ПЕРЕВІРКА ДОСТУПУ
    # current_user.id вже є ObjectId, тому ми просто передаємо його
    # group_oid тепер теж ObjectId
    membership = await GroupMembership.find_one({
        "user_id": current_user.id,
        "group_id": group_oid
    })

    if not membership:
        # Для дебагу: виведи в консоль, що саме шукав сервер
        print(f"DEBUG: Шукаю user={current_user.id} в group={group_oid}")
        raise HTTPException(status_code=403, detail="Ви не є учасником цієї групи")

    # 2. Фільтр Secret Gift (Isolation Rule-01)
    # Ховаємо подарунок, якщо поточний юзер є ціллю (target_user_id)
    query = {
        "group_id": group_id,
        "$nor": [
            {"is_secret_gift": True, "target_user_id": str(current_user.id)}
        ]
    }

    # 3. Отримання даних з пагінацією (BE-02)
    skip = (page - 1) * limit
    total = await Transaction.find(query).count()
    transactions = await Transaction.find(query).sort("-timestamp").skip(skip).limit(
        limit).to_list()

    # 4. Збагачення даними юзерів (ім'я/аватар)
    # Збираємо унікальні card_ids, щоб знайти власників
    items = []
    for tx in transactions:
        card = await BankCard.find_one({"account_id": tx.card_id})  # залежно від поля в моделі
        owner = await User.get(card.user_id) if card else None

        items.append(FeedTransactionItem(
            id=str(tx.id),
            amount=tx.amount,
            currency=tx.currency,
            description=tx.description,
            timestamp=tx.timestamp,
            display_name=owner.display_name if owner else "Unknown",
            avatar=owner.avatar if owner else None,
            card_masked_pan=card.masked_pan if card else "****"
        ))

    return FeedResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        has_more=(page * limit) < total
    )
