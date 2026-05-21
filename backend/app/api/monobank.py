from fastapi import APIRouter, Depends, status, HTTPException, Request
from app.services.monobank_service import MonobankService
from datetime import datetime
from decimal import Decimal

# АДАПТУЙ: імпортуй свою функцію отримання поточного юзера та модель User
from app.api.auth import get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from app.schemas.monobank import ConnectMonobankRequest, ConnectMonobankResponse, MonobankWebhookRequest
from app.models.bank_card import BankCard
router = APIRouter(prefix="/api/v1/monobank", tags=["Monobank Integration"])


@router.get("/webhook", status_code=status.HTTP_200_OK)
async def verify_monobank_webhook():
    """
    Ендпоінт для підтвердження вебхука від Монобанку.
    При реєстрації вебхука Монобанк відправляє GET-запит,
    щоб перевірити, чи сервер доступний і готовий приймати дані.
    """
    return {"message": "Webhook is ready"}

@router.post("/connect", status_code=status.HTTP_200_OK, response_model=ConnectMonobankResponse)
async def connect_monobank_card(
    request: ConnectMonobankRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Підключення картки Monobank через особистий API-токен.
    """
    # Сервіс тепер поверне словник з id, який FastAPI автоматично
    # перевірить на відповідність ConnectMonobankResponse
    return await MonobankService.connect_card(
        user_id=str(current_user.id),
        group_id=request.group_id,
        personal_token=request.personal_token
    )


@router.delete("/card/{card_id}", status_code=status.HTTP_200_OK)
async def disconnect_monobank_card(
    card_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Disconnect Monobank card (Soft delete).
    Transaction history remains intact.
    """
    result = await MonobankService.disconnect_card(
        card_id=card_id,
        user_id=str(current_user.id)
    )
    return result


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def handle_monobank_webhook(payload: MonobankWebhookRequest):
    """
    BE-01 & BE-02: Обробка вебхуків від Монобанку (реальні транзакції).
    """
    # 1. Знаходимо картку за account_id (Negative AC)
    card = await BankCard.find_one(BankCard.account_id == payload.data.account)
    if not card:
        # Повертаємо 200 OK, щоб Монобанк не повторював запити, але в базу не пишемо
        return {"status": "ignored", "detail": "Account not registered"}

    mono_tx = payload.data.statementItem

    # 2. Idempotency (BE-02): Захист від дублів
    existing_tx = await Transaction.find_one(Transaction.mono_id == mono_tx.id)
    if existing_tx:
        return {"status": "ignored", "detail": "Transaction already processed"}

    # 3. Підготовка даних (конвертація копійок у гривні, Unix-часу у datetime)
    amount_in_uah = Decimal(str(mono_tx.amount / 100))
    tx_time = datetime.fromtimestamp(mono_tx.time)

    # 4. Збереження транзакції (DB-01)
    new_transaction = Transaction(
        card_id=str(card.id),
        group_id=card.group_id,
        amount=amount_in_uah,
        currency="UAH",
        category_id="None",  # Змінимо на мапінг MCC в наступному кроці
        description=mono_tx.description,
        timestamp=tx_time,
        mono_id=mono_tx.id,
        mcc=mono_tx.mcc
    )

    await new_transaction.insert()

    # 5. Оновлення балансу картки
    card.balance = Decimal(str(mono_tx.balance / 100))
    await card.save()

    # TODO: BE-03 (WebSockets push піде сюди)

    return {"status": "success"}
