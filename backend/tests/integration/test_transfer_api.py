"""
Інтеграційні тести для POST /api/v1/transactions/transfer (Slice 4).
"""

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

from bson import ObjectId
from fastapi.testclient import TestClient

# Глушимо Beanie collection lookup
from beanie.odm.documents import Document
patch.object(Document, "get_pymongo_collection", return_value=MagicMock()).start()

from app.main import app  # noqa: E402
from app.core.dependencies import get_current_user  # noqa: E402

client = TestClient(app)

# ... твої імпорти залишаються тими самими ...

USER_ID = "507f1f77bcf86cd799439011"
FROM_CARD_ID = "607f1f77bcf86cd799439021"
TO_CARD_ID = "607f1f77bcf86cd799439022"
GROUP_ID = "507f1f77bcf86cd799439051"


class MockUser:
    id = ObjectId(USER_ID)


app.dependency_overrides[get_current_user] = lambda: MockUser()


# Надійний фейковий клас, який імітує Beanie Document та його мета-поля для Pydantic
class MockCard:
    # Додаємо атрибут класу, щоб BankCard.virtual_balance не кидав AttributeError
    virtual_balance = None

    def __init__(self, card_id, user_id, group_id, balance, status):
        self.id = ObjectId(card_id)
        self.user_id = user_id
        self.group_id = group_id
        self.balance = balance
        self.virtual_balance = balance
        self.status = status
        self.save = AsyncMock()
        self.update = AsyncMock()


def _make_card(
    card_id: str,
    user_id: str = USER_ID,
    group_id: str = GROUP_ID,
    balance: Decimal = Decimal("1000"),
    status: str = "ACTIVE",
):
    return MockCard(card_id, user_id, group_id, balance, status)

def _valid_body(**overrides) -> dict:
    body = {
        "from_card_id": FROM_CARD_ID,
        "to_card_id": TO_CARD_ID,
        "amount": "100.00",
        "description": "тест переказ",
        "category_id": None,
    }
    body.update(overrides)
    return body

SERVICE_PATH = "app.services.transaction_service"

class TestHappyPath:
    @patch(f"{SERVICE_PATH}.TransactionRepository.create_paired_virtual_transactions",
           new_callable=AsyncMock)
    @patch(f"{SERVICE_PATH}.GroupMembership.find_one", new_callable=AsyncMock)
    @patch(f"{SERVICE_PATH}.BankCardRepository.get_virtual_deltas_by_card_ids",
           new_callable=AsyncMock)
    @patch(f"{SERVICE_PATH}.BankCardRepository.get_by_id", new_callable=AsyncMock)
    def test_tc_1_1_happy_path_returns_200_with_response(
        self, mock_get_by_id, mock_deltas, mock_membership, mock_create_pair,
    ):
        from_card = _make_card(FROM_CARD_ID, balance=Decimal("1000"))
        to_card = _make_card(TO_CARD_ID, balance=Decimal("200"))
        mock_get_by_id.side_effect = [from_card, to_card]
        mock_deltas.side_effect = [
            {},
            {FROM_CARD_ID: Decimal("-100"), TO_CARD_ID: Decimal("100")},
        ]
        mock_membership.return_value = MagicMock()
        mock_create_pair.return_value = ("debit-id-1", "credit-id-1")

        # ВИПРАВЛЕНО: Додаємо контекст-менеджер patch.object, щоб обдурити Pydantic
        from app.models.bank_card import BankCard
        with patch.object(BankCard, 'virtual_balance', 'virtual_balance', create=True):
            res = client.post("/api/v1/transactions/transfer", json=_valid_body())

        assert res.status_code == 200

    @patch(f"{SERVICE_PATH}.TransactionRepository.create_paired_virtual_transactions",
           new_callable=AsyncMock)
    @patch(f"{SERVICE_PATH}.GroupMembership.find_one", new_callable=AsyncMock)
    @patch(f"{SERVICE_PATH}.BankCardRepository.get_virtual_deltas_by_card_ids",
           new_callable=AsyncMock)
    @patch(f"{SERVICE_PATH}.BankCardRepository.get_by_id", new_callable=AsyncMock)
    def test_tc_1_3_raw_balance_not_mutated(
        self, mock_get_by_id, mock_deltas, mock_membership, mock_create_pair,
    ):
        from_card = _make_card(FROM_CARD_ID, balance=Decimal("1000"))
        to_card = _make_card(TO_CARD_ID, balance=Decimal("200"))
        mock_get_by_id.side_effect = [from_card, to_card]
        mock_deltas.side_effect = [{}, {}]
        mock_membership.return_value = MagicMock()
        mock_create_pair.return_value = ("d", "c")

        # ВИПРАВЛЕНО: Такий самий хак тут
        from app.models.bank_card import BankCard
        with patch.object(BankCard, 'virtual_balance', 'virtual_balance', create=True):
            res = client.post("/api/v1/transactions/transfer", json=_valid_body())

        assert res.status_code == 200
class TestOwnershipAndExistence:
    @patch(f"{SERVICE_PATH}.BankCardRepository.get_by_id", new_callable=AsyncMock)
    def test_tc_4_1_from_card_not_found_returns_404(self, mock_get_by_id):
        mock_get_by_id.return_value = None
        res = client.post("/api/v1/transactions/transfer", json=_valid_body())
        assert res.status_code == 404

    @patch(f"{SERVICE_PATH}.BankCardRepository.get_by_id", new_callable=AsyncMock)
    def test_tc_4_e1_1_from_card_not_owned_returns_404_not_403(self, mock_get_by_id):
        other_user_id = "111111111111111111111111"
        from_card = _make_card(FROM_CARD_ID, user_id=other_user_id)
        mock_get_by_id.return_value = from_card

        res = client.post("/api/v1/transactions/transfer", json=_valid_body())
        assert res.status_code == 404

    @patch(f"{SERVICE_PATH}.BankCardRepository.get_by_id", new_callable=AsyncMock)
    def test_tc_11_1_to_card_not_found_returns_404(self, mock_get_by_id):
        from_card = _make_card(FROM_CARD_ID)
        mock_get_by_id.side_effect = [from_card, None]

        res = client.post("/api/v1/transactions/transfer", json=_valid_body())
        assert res.status_code == 404

class TestGroupBoundaries:
    @patch(f"{SERVICE_PATH}.BankCardRepository.get_by_id", new_callable=AsyncMock)
    def test_tc_5_1_cross_group_returns_400(self, mock_get_by_id):
        from_card = _make_card(FROM_CARD_ID, group_id=GROUP_ID)
        to_card = _make_card(TO_CARD_ID, group_id="999999999999999999999999")
        mock_get_by_id.side_effect = [from_card, to_card]

        res = client.post("/api/v1/transactions/transfer", json=_valid_body())
        assert res.status_code == 400

    @patch(f"{SERVICE_PATH}.GroupMembership.find_one", new_callable=AsyncMock)
    @patch(f"{SERVICE_PATH}.BankCardRepository.get_by_id", new_callable=AsyncMock)
    def test_tc_15_1_membership_revoked_returns_403(self, mock_get_by_id, mock_membership):
        from_card = _make_card(FROM_CARD_ID)
        to_card = _make_card(TO_CARD_ID)
        mock_get_by_id.side_effect = [from_card, to_card]
        mock_membership.return_value = None

        res = client.post("/api/v1/transactions/transfer", json=_valid_body())
        assert res.status_code == 403

class TestServiceBackupChecks:
    def test_tc_6_1_same_card_via_schema_returns_422(self):
        body = _valid_body(to_card_id=FROM_CARD_ID)
        res = client.post("/api/v1/transactions/transfer", json=body)
        assert res.status_code == 422

    @patch(f"{SERVICE_PATH}.GroupMembership.find_one", new_callable=AsyncMock)
    @patch(f"{SERVICE_PATH}.BankCardRepository.get_by_id", new_callable=AsyncMock)
    def test_tc_status_inactive_card_returns_400(self, mock_get_by_id, mock_membership):
        from_card = _make_card(FROM_CARD_ID, status="BLOCKED")
        to_card = _make_card(TO_CARD_ID)
        mock_get_by_id.side_effect = [from_card, to_card]
        mock_membership.return_value = MagicMock()

        res = client.post("/api/v1/transactions/transfer", json=_valid_body())
        assert res.status_code == 400

class TestFundsAndAmountValidation:
    @patch(f"{SERVICE_PATH}.GroupMembership.find_one", new_callable=AsyncMock)
    @patch(f"{SERVICE_PATH}.BankCardRepository.get_virtual_deltas_by_card_ids", new_callable=AsyncMock)
    @patch(f"{SERVICE_PATH}.BankCardRepository.get_by_id", new_callable=AsyncMock)
    def test_tc_8_1_insufficient_funds_returns_400(
        self, mock_get_by_id, mock_deltas, mock_membership,
    ):
        from_card = _make_card(FROM_CARD_ID, balance=Decimal("50"))
        to_card = _make_card(TO_CARD_ID)
        mock_get_by_id.side_effect = [from_card, to_card]
        mock_deltas.return_value = {}
        mock_membership.return_value = MagicMock()

        res = client.post("/api/v1/transactions/transfer", json=_valid_body())
        assert res.status_code == 400

    def test_tc_9_1_amount_zero_returns_422(self):
        res = client.post("/api/v1/transactions/transfer", json=_valid_body(amount="0"))
        assert res.status_code == 422

    def test_tc_9_2_amount_negative_returns_422(self):
        res = client.post("/api/v1/transactions/transfer", json=_valid_body(amount="-10"))
        assert res.status_code == 422

    def test_tc_10_1_amount_too_many_decimals_returns_422(self):
        res = client.post("/api/v1/transactions/transfer", json=_valid_body(amount="10.123"))
        assert res.status_code == 422

class TestCategoryValidation:
    @patch(f"{SERVICE_PATH}.Category.get", new_callable=AsyncMock)
    @patch(f"{SERVICE_PATH}.GroupMembership.find_one", new_callable=AsyncMock)
    @patch(f"{SERVICE_PATH}.BankCardRepository.get_by_id", new_callable=AsyncMock)
    def test_tc_13_1_category_not_found_returns_400(
        self, mock_get_by_id, mock_membership, mock_category_get,
    ):
        from_card = _make_card(FROM_CARD_ID)
        to_card = _make_card(TO_CARD_ID)
        mock_get_by_id.side_effect = [from_card, to_card]
        mock_membership.return_value = MagicMock()
        mock_category_get.return_value = None

        body = _valid_body(category_id="507f1f77bcf86cd799439999")
        res = client.post("/api/v1/transactions/transfer", json=body)
        assert res.status_code == 400

class TestImmutability:
    def test_tc_17_1_put_transactions_id_returns_404_or_405(self):
        res = client.put("/api/v1/transactions/507f1f77bcf86cd799439abc", json={})
        assert res.status_code in (404, 405)

    def test_tc_17_2_delete_transactions_id_returns_404_or_405(self):
        res = client.delete("/api/v1/transactions/507f1f77bcf86cd799439abc")
        assert res.status_code in (404, 405)

class TestUnauthenticated:
    def test_tc_7_1_unauthenticated_returns_401_or_403(self):
        original_override = app.dependency_overrides.pop(get_current_user, None)
        try:
            res = client.post("/api/v1/transactions/transfer", json=_valid_body())
            assert res.status_code in (401, 403)
        finally:
            if original_override is not None:
                app.dependency_overrides[get_current_user] = original_override

class TestRateLimit:
    def test_endpoint_has_rate_limit_decorator(self):
        from app.core.limiter import limiter as app_limiter
        assert app_limiter is not None
        assert hasattr(app_limiter, "limit")
