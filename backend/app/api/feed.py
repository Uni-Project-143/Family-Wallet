from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timezone
from app.api.auth import get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from app.models.bank_card import BankCard
from app.models.group_membership import GroupMembership
from app.models.category import Category
from app.models.gift_event import GiftEvent
from app.schemas.feed import FeedResponse, FeedTransactionItem
from beanie import PydanticObjectId
import urllib.parse

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

    # 4. Фільтр Secret Gift (PROJ-58: Ізоляція Target User)
    now = datetime.now(timezone.utc)

    # Крок А: Шукаємо подарунки, де юзер є іменинником, але час ще НЕ настав
    locked_gifts = await GiftEvent.find(
        GiftEvent.target_user_id == str(current_user.id),
        GiftEvent.unlock_date > now
    ).to_list()

        # Витягуємо їхні ID у список
    locked_gift_ids = [str(g.id) for g in locked_gifts]

        # Крок Б: Формуємо запит.
    query = {
        "group_id": clean_group_id,
         "$nor": [
            # 1. Захист для старих транзакцій (без прив'язки до події)
            {"is_secret_gift": True, "target_user_id": str(current_user.id), "gift_id": None},
            # 2. Нове правило (BE-02): Приховуємо транзакції, якщо вони належать до заблокованих подій
            {"gift_id": {"$in": locked_gift_ids}}
        ]
    }

    # 5. Отримання даних з пагінацією (BE-02)
    skip = (page - 1) * limit
    total = await Transaction.find(query).count()
    transactions = await Transaction.find(query).sort("-timestamp").skip(skip).limit(limit).to_list()

    # 6. Збагачення даними юзерів (ім'я/аватар/категорії)
    items = []
    for tx in transactions:
        card = None
        if tx.card_id:
            try:
                card = await BankCard.get(PydanticObjectId(tx.card_id))
            except Exception:
                pass

        owner = None
        if card and card.user_id:
            try:
                owner = await User.get(PydanticObjectId(card.user_id))
            except Exception:
                pass

        category = None
        if tx.category_id and tx.category_id != "None" and tx.category_id.strip() != "":
            try:
                category = await Category.get(PydanticObjectId(tx.category_id))
            except Exception:
                pass

        # ==========================================
        # НОВА ЛОГІКА ІДЕНТИФІКАЦІЇ (Fallback Logic)
        # ==========================================
        if owner:
            # Якщо full_name пусте, беремо email, якщо і він пустий - "Без імені"
            display_name = owner.full_name or getattr(owner, 'email', None) or "Без імені"

            # Якщо є avatar_url з бази - беремо його. Якщо ні - генеруємо аватар з ініціалами.
            avatar_url = getattr(owner, 'avatar_url', None)
            if avatar_url:
                avatar = avatar_url
            else:
                # url-encode для безпечної передачі українських літер та пробілів
                safe_name = urllib.parse.quote(display_name)
                avatar = f"https://ui-avatars.com/api/?name={safe_name}&background=random&color=fff&size=128"
        else:
            # Negative AC: Транзакція без прив'язки до user
            display_name = "Невідомий учасник"
            # Сірий аватар зі знаком питання
            avatar = "https://ui-avatars.com/api/?name=?&background=808080&color=fff&size=128"

        # Формуємо фінальний об'єкт для фронтенду
        items.append(FeedTransactionItem(
            id=str(tx.id),
            amount=float(tx.amount),
            currency=tx.currency,
            description=tx.description or "Без опису",
            timestamp=tx.timestamp,
            display_name=display_name,  # <-- Оновлено
            avatar=avatar,  # <-- Оновлено
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
