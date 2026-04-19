from fastapi import APIRouter
import logging

logger = logging.getLogger("FamilyWallet")
router = APIRouter()


@router.post("/anonymous", tags=["Gifts"])
async def send_anonymous_gift(trigger_crash: bool = False):
    """Анонімний подарунок з тестом обробника помилок."""
    if trigger_crash:
        crash = 1 / 0  # Тест Global Exception Handler

    return {"message": "Скелет: Анонімний подарунок успішно надіслано"}
