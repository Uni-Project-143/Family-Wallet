from beanie import Document, free_fall_migration
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional
from pydantic import Field
import uuid

class User(Document):
    full_name: str
    email: str
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    avatar_url: Optional[str] = None
    fcm_token: Optional[str] = None

    class Settings:
        name = "users"


class Category(Document):
    name: str
    icon: str
    color: str
    mcc_list: List[int] = []

    class Settings:
        name = "categories"


class BankCard(Document):
    user_id: str
    group_id: str
    encrypted_token: str
    account_id: str
    masked_pan: str
    balance: Decimal
    virtual_balance: Decimal = Decimal("0.00")
    status: str = "ACTIVE"
    transaction_ids: List[str] = []

    class Settings:
        name = "bank_cards"


class Transaction(Document):
    card_id: str
    group_id: str
    amount: Decimal
    currency: str = "UAH"
    category_id: Optional[str] = None
    description: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reactions: List[dict] = []
    is_secret_gift: bool = False
    target_user_id: Optional[str] = None
    gift_id: Optional[str] = None
    is_virtual: bool = False
    transfer_id: Optional[str] = None

    class Settings:
        name = "transactions"


class Group(Document):
    name: str
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "groups"


class GroupMembership(Document):
    user_id: str
    group_id: str
    role: str
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "group_memberships"


class InviteToken(Document):
    group_id: str
    token: str = Field(default_factory=lambda: uuid.uuid4().hex)
    created_by: str
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=48))
    used_at: Optional[datetime] = None

    class Settings:
        name = "invite_tokens"


class GiftEvent(Document):
    name: str
    organizer_id: str
    target_user_id: str
    group_id: str
    goal_amount: float
    unlock_date: datetime
    status: str = "ACTIVE"
    secret_mode: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "gift_events"


class MoneyRequest(Document):
    requester_id: str
    recipient_id: str
    group_id: str
    amount: Decimal
    description: str
    status: str = "PENDING"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "money_requests"


ALL_MODELS = [
    User, Category, BankCard, Transaction, Group, GroupMembership,
    InviteToken, GiftEvent, MoneyRequest
]

class Forward:
    @free_fall_migration(document_models=ALL_MODELS)
    async def create_and_seed(self, session):
        now = datetime.now(timezone.utc)

        cat_food = Category(name="Продукти", icon="🛒", color="#FF5733", mcc_list=[5411, 5499])
        cat_cafe = Category(name="Кафе та ресторани", icon="🍔", color="#FFC300",
                            mcc_list=[5812, 5814, 5811])
        cat_transport = Category(name="Транспорт", icon="🚗", color="#33FF57",
                                 mcc_list=[4111, 4121, 4131, 4789])
        cat_entertainment = Category(name="Розваги", icon="🎬", color="#3357FF",
                                     mcc_list=[7832, 7922, 7999])
        cat_gifts = Category(name="Подарунки", icon="🎁", color="#FF33A1", mcc_list=[5947])
        cat_transfers = Category(name="Перекази", icon="💸", color="#808080", mcc_list=[4829])

        await Category.insert_many(
            [cat_food, cat_cafe, cat_transport, cat_entertainment, cat_gifts, cat_transfers],
            session=session
        )

        hashed_pw = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjIQ68YbaS"

        user_admin = User(
            full_name="Олександр (Адмін)",
            email="admin@familywallet.com",
            hashed_password=hashed_pw
        )
        user_member = User(
            full_name="Володимир (Учасник)",
            email="member@familywallet.com",
            hashed_password=hashed_pw
        )

        await user_admin.insert(session=session)
        await user_member.insert(session=session)

        group = Group(
            name="Сімейний Бюджет",
            created_by=str(user_admin.id)
        )
        await group.insert(session=session)

        admin_membership = GroupMembership(
            user_id=str(user_admin.id),
            group_id=str(group.id),
            role="ADMIN"
        )
        member_membership = GroupMembership(
            user_id=str(user_member.id),
            group_id=str(group.id),
            role="MEMBER"
        )
        await GroupMembership.insert_many([admin_membership, member_membership], session=session)

        card_admin = BankCard(
            user_id=str(user_admin.id),
            group_id=str(group.id),
            encrypted_token="encrypted_dummy_token_1",
            account_id="mono_account_admin_123",
            masked_pan="•••• 4321",
            balance=Decimal("25400.00"),
            virtual_balance=Decimal("25400.00"),
        )
        card_member = BankCard(
            user_id=str(user_member.id),
            group_id=str(group.id),
            encrypted_token="encrypted_dummy_token_2",
            account_id="mono_account_member_456",
            masked_pan="•••• 8765",
            balance=Decimal("5000.00"),
            virtual_balance=Decimal("5000.00"),
        )
        await BankCard.insert_many([card_admin, card_member], session=session)

        yesterday = now - timedelta(days=1)
        last_week = now - timedelta(days=7)

        t1 = Transaction(
            card_id=str(card_admin.id),
            group_id=str(group.id),
            amount=Decimal("-850.00"),
            category_id=str(cat_food.id),
            description="Сільпо (Закупівля на тиждень)",
            timestamp=now,
            reactions=[{"user_id": str(user_member.id), "emoji": "👍", "created_at": now}]
        )

        t2 = Transaction(
            card_id=str(card_member.id),
            group_id=str(group.id),
            amount=Decimal("-350.00"),
            category_id=str(cat_cafe.id),
            description="McDonalds",
            timestamp=yesterday,
        )

        transfer_id = str(uuid.uuid4())
        vt_debit = Transaction(
            card_id=str(card_admin.id),
            group_id=str(group.id),
            amount=Decimal("-500.00"),
            category_id=str(cat_transfers.id),
            description="Скинув на кишенькові",
            timestamp=last_week,
            is_virtual=True,
            transfer_id=transfer_id
        )
        vt_credit = Transaction(
            card_id=str(card_member.id),
            group_id=str(group.id),
            amount=Decimal("500.00"),
            category_id=str(cat_transfers.id),
            description="Отримано кишенькові",
            timestamp=last_week,
            is_virtual=True,
            transfer_id=transfer_id
        )

        await Transaction.insert_many([t1, t2, vt_debit, vt_credit], session=session)

        gift = GiftEvent(
            name="Новий ноутбук для Володимира",
            organizer_id=str(user_admin.id),
            target_user_id=str(user_member.id),
            group_id=str(group.id),
            goal_amount=30000.0,
            unlock_date=now + timedelta(days=5),
            status="ACTIVE"
        )
        await gift.insert(session=session)

        gift_tx = Transaction(
            card_id=str(card_admin.id),
            group_id=str(group.id),
            amount=Decimal("-2000.00"),
            category_id=str(cat_gifts.id),
            description=f"Внесок до Secret Gift: {gift.name}",
            timestamp=now,
            is_secret_gift=True,
            target_user_id=str(user_member.id),
            gift_id=str(gift.id),
            is_virtual=True
        )
        await gift_tx.insert(session=session)

        request = MoneyRequest(
            requester_id=str(user_member.id),
            recipient_id=str(user_admin.id),
            group_id=str(group.id),
            amount=Decimal("200.00"),
            description="На каву ☕",
            status="PENDING",
            created_at=now
        )
        await request.insert(session=session)


class Backward:
    @free_fall_migration(document_models=ALL_MODELS)
    async def rollback(self, session):
        for model in ALL_MODELS:
            await model.find_all().delete(session=session)
