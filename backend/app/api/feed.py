from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.auth import get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from app.models.bank_card import BankCard
from app.models.group_membership import GroupMembership
from app.models.category import Category
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
    # 1. Очищаємо рядок (щоб Swagger не ламав запит випадковими лапками)
    clean_group_id = group_id.strip(' "\'\n')

    # 2. КОНВЕРТУЄМО очищений group_id в ObjectId
    try:
        group_oid = PydanticObjectId(clean_group_id)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Невалідний ID групи: {clean_group_id}")

    # 3. ПЕРЕВІРКА ДОСТУПУ
    membership = await GroupMembership.find_one({
        "user_id": current_user.id,
        "group_id": group_oid
    })

    if not membership:
        print(f"DEBUG: Шукаю user={current_user.id} в group={group_oid}")
        raise HTTPException(status_code=403, detail="Ви не є учасником цієї групи")

    # 4. Фільтр Secret Gift (Isolation Rule-01)
    query = {
        "group_id": clean_group_id,
        "$nor": [
            {"is_secret_gift": True, "target_user_id": str(current_user.id)}
        ]
    }

    # 5. Отримання даних з пагінацією (BE-02)
    skip = (page - 1) * limit
    total = await Transaction.find(query).count()
    transactions = await Transaction.find(query).sort("-timestamp").skip(skip).limit(limit).to_list()

    # 6. Збагачення даними юзерів (ім'я/аватар/категорії)
    items = []
    for tx in transactions:
        # ВИПРАВЛЕНО БАГ 2: Шукаємо картку за ObjectId
        card = None
        if tx.card_id:
            try:
                card = await BankCard.get(PydanticObjectId(tx.card_id))
            except Exception:
                pass

        # ВИПРАВЛЕНО БАГ 3: Безпечне отримання Юзера
        owner = None
        if card and card.user_id:
            try:
                owner = await User.get(PydanticObjectId(card.user_id))
            except Exception:
                pass

        # ДОДАНО: Підтягуємо категорію для іконки
        category = None
        if tx.category_id and tx.category_id != "None" and tx.category_id.strip() != "":
            try:
                category = await Category.get(PydanticObjectId(tx.category_id))
            except Exception:
                pass

        # Формуємо фінальний об'єкт для фронтенду
        items.append(FeedTransactionItem(
            id=str(tx.id),
            amount=float(tx.amount), # Конвертуємо Decimal у float
            currency=tx.currency,
            description=tx.description or "Без опису",
            timestamp=tx.timestamp,
            display_name=owner.full_name if owner else "Unknown",
            avatar=getattr(owner, 'avatar_url', None) if owner else None,
            card_masked_pan=card.masked_pan if card else "****",
            author_id=str(owner.id) if owner else None,
            category_name=category.name if category else "Інше",
            category_emoji=category.icon if category else "💰",
            is_secret_gift=tx.is_secret_gift
        ))

    return FeedResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        has_more=(page * limit) < total
    )
