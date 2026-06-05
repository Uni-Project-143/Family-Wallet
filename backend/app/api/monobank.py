import os

from fastapi import APIRouter, Depends, status, HTTPException, Request
from app.services.monobank_service import MonobankService
from datetime import datetime
from decimal import Decimal
import httpx
from typing import List
from beanie.odm.operators.update.general import Set, Inc

# АДАПТУЙ: імпортуй свою функцію отримання поточного юзера та модель User
from app.api.auth import get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from app.schemas.monobank import ConnectMonobankRequest, ConnectMonobankResponse, MonobankWebhookRequest, ClientInfoRequest, CardInfoResponse
from app.models.bank_card import BankCard
from app.core.websockets import ws_manager
from app.models.category import Category


def get_category_id_by_mcc(mcc: int) -> str:
    """Перекладає код Монобанку у нашу текстову категорію для фронтенду"""
    mcc_mapping = {
        5411: "groceries",     # Супермаркети (Сільпо, АТБ)
        5814: "fast_food",     # Фастфуд, кафе
        5912: "pharmacy",      # Аптеки
        7999: "entertainment", # Розваги
        5541: "transport",     # АЗС
        4121: "transport",     # Таксі
    }
    return mcc_mapping.get(mcc, "other") # Якщо код невідомий, буде "other"


router = APIRouter(prefix="/api/v1/monobank", tags=["Monobank Integration"])


@router.get("/webhook", status_code=status.HTTP_200_OK)
async def verify_monobank_webhook():
    """
    Ендпоінт для підтвердження вебхука від Монобанку.
    При реєстрації вебхука Монобанк відправляє GET-запит,
    щоб перевірити, чи сервер доступний і готовий приймати дані.
    """
    return {"message": "Webhook is ready"}


@router.post("/connect", status_code=status.HTTP_200_OK)
async def connect_monobank_card(
    request: ConnectMonobankRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Фінальне підключення обраної картки до групи.
    Встановлює вебхук у Монобанку та зберігає картку в БД.
    """
    # 1. Перевіряємо, чи немає вже такої картки в базі (щоб не було дублікатів)
    existing_card = await BankCard.find_one(BankCard.account_id == request.account_id)
    if existing_card:
        raise HTTPException(status_code=409,
                            detail="This account is already connected to the system.")

    # 2. Реєструємо Webhook у Монобанку.
    # URL береться з env MONOBANK_WEBHOOK_URL (для прода — публічний https-домен бекенду).
    webhook_url = os.getenv("MONOBANK_WEBHOOK_URL")
    if not webhook_url:
        raise HTTPException(
            status_code=500,
            detail="MONOBANK_WEBHOOK_URL is not configured on the server."
        )

    async with httpx.AsyncClient() as client:
        wh_response = await client.post(
            "https://api.monobank.ua/personal/webhook",
            headers={"X-Token": request.personal_token},
            json={"webHookUrl": webhook_url}
        )
        if wh_response.status_code not in (200, 201) and wh_response.status_code != 429:
            raise HTTPException(status_code=400, detail="Failed to register webhook in Monobank")

    # 3. Зберігаємо картку в нашу базу
    new_card = BankCard(
        user_id=str(current_user.id),
        group_id=request.group_id,
        encrypted_token=request.personal_token,
        account_id=request.account_id,
        masked_pan=request.masked_pan,
        balance=request.balance,
        virtual_balance=request.balance,
        status="ACTIVE"
    )
    await new_card.insert()

    return {
        "status": "success",
        "message": "Card successfully connected",
        "card_id": str(new_card.id)
    }


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

    print(f"\n[DEBUG] Отримано вебхук для акаунту: {payload.data.account}")

    # 1. Знаходимо картку за account_id (Negative AC)
    card = await BankCard.find_one(BankCard.account_id == payload.data.account)
    if not card:
        # Повертаємо 200 OK, щоб Монобанк не повторював запити, але в базу не пишемо
        return {"status": "ignored", "detail": "Account not registered"}

    mono_tx = payload.data.statementItem

    # 2. Idempotency (BE-02): Захист від дублів
    existing_tx = await Transaction.find_one(Transaction.mono_id == mono_tx.id)
    if existing_tx:
        print(f"[DEBUG] Транзакція {mono_tx.id} ВЖЕ Є в БД! Ігноруємо (Idempotency).")
        return {"status": "ignored", "detail": "Transaction already processed"}

    print("[DEBUG] Все ок, зберігаємо транзакцію і пушимо в сокет!")

    # 3. Підготовка даних (конвертація копійок у гривні, Unix-часу у datetime)
    amount_in_uah = Decimal(str(mono_tx.amount / 100))
    tx_time = datetime.fromtimestamp(mono_tx.time)

    resolved_category_id = get_category_id_by_mcc(mono_tx.mcc)

    # 4. Збереження транзакції (DB-01)
    new_transaction = Transaction(
        card_id=str(card.id),
        group_id=card.group_id,
        amount=amount_in_uah,
        currency="UAH",
        category_id=resolved_category_id,
        description=mono_tx.description,
        timestamp=tx_time,
        mono_id=mono_tx.id,
        mcc=mono_tx.mcc
    )

    await new_transaction.insert()

    # 5. Оновлення балансу картки.
    # Новий реальний баланс рахунку приходить у mono_tx.balance (копійки),
    # а mono_tx.amount — це сума самої операції (НЕ підсумковий баланс).
    new_raw_balance = Decimal(str(mono_tx.balance / 100))

    balance_diff = new_raw_balance - card.balance

    await card.update(
        Set({BankCard.balance: new_raw_balance}),
        Inc({BankCard.virtual_balance: float(balance_diff)})
    )

    ws_payload = {
        "event": "new_transaction",
        "data": {
            "id": str(new_transaction.id),
            "amount": float(new_transaction.amount),
            "currency": new_transaction.currency,
            "description": new_transaction.description,
            "category_id": new_transaction.category_id,
            "timestamp": new_transaction.timestamp.isoformat(),
        }
    }

    # Магія: пушимо в кімнату групи (Real-time!)
    await ws_manager.broadcast_to_group(str(card.group_id), ws_payload)

    return {"status": "success"}


@router.post("/client-info", status_code=status.HTTP_200_OK, response_model=List[CardInfoResponse])
async def get_monobank_client_info(request: ClientInfoRequest):
    """
    Отримує список всіх карток клієнта з Monobank API.
    УВАГА: Monobank дозволяє цей запит лише 1 раз на 60 секунд!
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.monobank.ua/personal/client-info",
            headers={"X-Token": request.personal_token}
        )

        if response.status_code == 429:
            raise HTTPException(status_code=429,
                                detail="Занадто багато запитів до Монобанку. Зачекайте 1 хвилину.")
        elif response.status_code != 200:
            raise HTTPException(status_code=400, detail="Невалідний токен або помилка Monobank API")

        data = response.json()
        cards = []

        # Монобанк повертає масив 'accounts'
        for acc in data.get("accounts", []):
            # Фільтруємо лише гривневі картки (код 980)
            if acc.get("currencyCode") == 980:
                # У Монобанку maskedPan - це масив, беремо перший елемент
                masked_pan_list = acc.get("maskedPan", [])
                masked_pan = masked_pan_list[0] if masked_pan_list else "Unknown"

                cards.append(CardInfoResponse(
                    account_id=acc.get("id"),
                    masked_pan=masked_pan,
                    type=acc.get("type", "unknown"),
                    balance=Decimal(str(acc.get("balance", 0) / 100)),
                    currency=980
                ))

        return cards
