from fastapi import APIRouter, HTTPException
import logging

logger = logging.getLogger("FamilyWallet")
router = APIRouter()

@router.post("/", tags=["Wallet"])
async def create_wallet():
    """Створення нового спільного гаманця."""
    return {"message": "Скелет: Гаманець успішно створено", "wallet_id": "12345"}

@router.get("/{wallet_id}", tags=["Wallet"])
async def get_wallet_summary(wallet_id: str):
    """Отримання балансу (додатковий логічний ендпоінт)."""
    return {
        "wallet_id": wallet_id,
        "balance": 0.00,
        "currency": "UAH"
    }

@router.post("/{wallet_id}/transactions", tags=["Transactions"])
async def add_transaction(wallet_id: str, amount: float):
    """Додавання транзакції."""
    if amount == 0:
        raise HTTPException(
            status_code=400,
            detail="Сума транзакції не може бути нульовою."
        )
    return {"message": f"Скелет: Транзакція на суму {amount} додана до гаманця {wallet_id}"}
