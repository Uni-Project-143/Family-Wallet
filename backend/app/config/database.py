import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.models.category import Category
from app.models.gift_event import GiftEvent
# Імпортуємо моделі
from app.models.user import User
from app.models.invite import InviteToken
from app.models.group import Group
from app.models.group_membership import GroupMembership
from app.models.blacklisted_token import BlacklistedToken
from app.models.bank_card import BankCard
from app.models.transaction import Transaction

load_dotenv()

MONGO_URL = os.getenv("MONGO_ATLAS")
DB_NAME = os.getenv("DB_NAME", "FamilyWallet")

if not MONGO_URL:
    raise RuntimeError(
        "MONGO_ATLAS env variable is not set. "
        "Define connection string to MongoDB Atlas before starting the app."
    )

# ==========================================================
# 🛠️ ХАК (Monkey Patch) ДЛЯ ВИРІШЕННЯ КОНФЛІКТУ BEANIE ТА MOTOR
# Додаємо порожній метод, щоб Beanie не видавав TypeError
# ==========================================================
if not hasattr(AsyncIOMotorClient, "append_metadata"):
    AsyncIOMotorClient.append_metadata = lambda self, *args, **kwargs: None

# Створюємо підключення до БД
db_client = AsyncIOMotorClient(MONGO_URL)

async def init_db():
    """Функція підключає моделі Beanie до MongoDB при старті сервера."""
    await init_beanie(
        database=db_client[DB_NAME],
        document_models=[User, Group, GroupMembership, InviteToken, BlacklistedToken, BankCard, Transaction, Category, GiftEvent]
    )
