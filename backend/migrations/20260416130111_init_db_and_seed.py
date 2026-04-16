from beanie import Document, free_fall_migration
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import Field

# --- Snapshot Models ---

class User(Document):
    full_name: str
    email: str
    password_hash: str
    role: str
    bankcard_ids: List[str] = []
    class Settings:
        name = "users"

class Category(Document):
    name: str
    icon: str
    color: str
    class Settings:
        name = "categories"

class BankCard(Document):
    user_id: str
    bank_token: str
    masked_pan: str
    balance: Decimal
    transaction_ids: List[str] = []
    class Settings:
        name = "bank_cards"

class Transaction(Document):
    card_id: str
    amount: Decimal
    currency: str
    category_id: str
    description: str
    timestamp: datetime
    reactions: List[dict] = []
    class Settings:
        name = "transactions"

class Group(Document):
    name: str
    invite_link: str
    member_ids: List[str] = []
    gift_event_ids: List[str] = []
    class Settings:
        name = "groups"

class GiftEvent(Document):
    organizer_id: str
    target_user_id: str
    name: str
    unlock_date: datetime
    status: str
    class Settings:
        name = "gift_events"

class MoneyRequest(Document):
    requester_id: str
    recipient_id: str
    group_id: str
    amount: Decimal
    description: str
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    class Settings:
        name = "money_requests"

class VirtualTransfer(Document):
    money_request_id: str
    sender_id: str
    recipient_id: str
    group_id: str
    amount: Decimal
    currency: str
    created_at: datetime
    class Settings:
        name = "virtual_transfers"


class Forward:
    @free_fall_migration(document_models=[
        User, Category, BankCard, Transaction, Group, GiftEvent, MoneyRequest, VirtualTransfer
    ])
    async def create_and_seed(self, session):
        # 1. Categories (Baseline)
        cat_food = Category(name="Food", icon="fastfood", color="#FF5733")
        cat_transport = Category(name="Transport", icon="directions_bus", color="#3357FF")
        cat_gifts = Category(name="Gifts", icon="redeem", color="#FF33A1")
        await cat_food.insert(session=session)
        await cat_transport.insert(session=session)
        await cat_gifts.insert(session=session)

        # 2. Users (Seed Data)
        user_main = User(
            full_name="Гелеван Олександр Віталійович",
            email="oleksandr@familywallet.app",
            password_hash="argon2_hashed_password_here",
            role="Admin"
        )
        user_member = User(
            full_name="Володимир Тестовий",
            email="volodymyr@familywallet.app",
            password_hash="argon2_hashed_password_here",
            role="Member"
        )
        await user_main.insert(session=session)
        await user_member.insert(session=session)

        # 3. Groups
        group = Group(
            name="Гелеван Family",
            invite_link="https://familywallet.app/join/xyz123",
            member_ids=[str(user_main.id), str(user_member.id)]
        )
        await group.insert(session=session)

        # 4. Bank Cards
        card = BankCard(
            user_id=str(user_main.id),
            bank_token="mono_api_token_sample",
            masked_pan="4441********1111",
            balance=Decimal("25400.50")
        )
        await card.insert(session=session)

        # 5. Transactions
        t1 = Transaction(
            card_id=str(card.id),
            amount=Decimal("-450.00"),
            currency="UAH",
            category_id=str(cat_food.id),
            description="Сільпо",
            timestamp=datetime.utcnow(),
            reactions=[{"user_id": str(user_member.id), "emoji_code": "👍"}]
        )
        await t1.insert(session=session)

        # 6. Money Requests & Transfers
        request = MoneyRequest(
            requester_id=str(user_member.id),
            recipient_id=str(user_main.id),
            group_id=str(group.id),
            amount=Decimal("200.00"),
            description="На каву в офісі",
            status="Accepted",
            created_at=datetime.utcnow(),
            resolved_at=datetime.utcnow()
        )
        await request.insert(session=session)

        transfer = VirtualTransfer(
            money_request_id=str(request.id),
            sender_id=str(user_main.id),
            recipient_id=str(user_member.id),
            group_id=str(group.id),
            amount=Decimal("200.00"),
            currency="UAH",
            created_at=datetime.utcnow()
        )
        await transfer.insert(session=session)

class Backward:
    @free_fall_migration(document_models=[
        User, Category, BankCard, Transaction, Group, GiftEvent, MoneyRequest, VirtualTransfer
    ])
    async def rollback(self, session):
        # Видаляємо всі дані з усіх колекцій при відкаті
        models = [User, Category, BankCard, Transaction, Group, GiftEvent, MoneyRequest, VirtualTransfer]
        for model in models:
            await model.find_all().delete(session=session)
