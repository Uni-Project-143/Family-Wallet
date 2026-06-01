"""
Інтеграційні тести для GET /api/v1/bank-cards/group/{group_id}.

Покриває UC-2 (effective_balance), AC-02 та AC-11:
  * Внутрішні віртуальні транзакції (is_virtual=True) додаються до raw balance,
    формуючи effective_balance, який повертається у відповіді API.
  * Raw card.balance залишається незмінним (read-only).
"""

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

from bson import ObjectId
from fastapi.testclient import TestClient

from app.main import app
from app.core.dependencies import get_current_user

client = TestClient(app)


class MockUser:
    id = ObjectId("507f1f77bcf86cd799439011")


app.dependency_overrides[get_current_user] = lambda: MockUser()


def _build_card(card_id: str, balance: Decimal) -> MagicMock:
    """Створює мок BankCard з усіма потрібними полями для відповіді API."""
    card = MagicMock()
    card.id = ObjectId(card_id)
    card.user_id = "507f1f77bcf86cd799439011"
    card.group_id = "607f1f77bcf86cd799439022"
    card.account_id = "acc-" + card_id[-4:]
    card.masked_pan = "**** **** **** 1234"
    card.balance = balance
    card.status = "ACTIVE"
    card.transaction_ids = []
    return card


def _mock_card_find_cursor(cards: list) -> MagicMock:
    cursor = AsyncMock()
    cursor.to_list.return_value = cards
    return cursor


def _mock_owner() -> MagicMock:
    owner = MagicMock()
    owner.full_name = "Власник Картки"
    return owner


GROUP_ID = "607f1f77bcf86cd799439022"


class TestEffectiveBalance:
    """Тести логіки effective_balance = balance + Σ virtual amounts."""

    @patch("app.api.bank_card.BankCardRepository.get_virtual_deltas_by_card_ids", new_callable=AsyncMock)
    @patch("app.api.bank_card.User.get", new_callable=AsyncMock)
    @patch("app.api.bank_card.BankCard.find")
    @patch("app.api.bank_card.GroupMembership.find_one", new_callable=AsyncMock)
    def test_tc_2_1_effective_balance_with_negative_delta(
        self, mock_membership, mock_card_find, mock_user_get, mock_deltas
    ):
        """TC-2.1: balance=1000, delta=-100 → effective_balance=900."""
        card_id = "707f1f77bcf86cd799439033"
        card = _build_card(card_id, Decimal("1000"))

        mock_membership.return_value = True
        mock_card_find.return_value = _mock_card_find_cursor([card])
        mock_user_get.return_value = _mock_owner()
        mock_deltas.return_value = {card_id: Decimal("-100")}

        res = client.get(f"/api/v1/bank-cards/group/{GROUP_ID}")

        assert res.status_code == 200
        body = res.json()
        assert len(body) == 1
        assert Decimal(body[0]["balance"]) == Decimal("1000")
        assert Decimal(body[0]["effective_balance"]) == Decimal("900")
        # AC-11: raw balance НЕ мутується кодом ендпоінта
        assert card.balance == Decimal("1000")

    @patch("app.api.bank_card.BankCardRepository.get_virtual_deltas_by_card_ids", new_callable=AsyncMock)
    @patch("app.api.bank_card.User.get", new_callable=AsyncMock)
    @patch("app.api.bank_card.BankCard.find")
    @patch("app.api.bank_card.GroupMembership.find_one", new_callable=AsyncMock)
    def test_tc_2_a1_1_no_virtual_tx_effective_equals_balance(
        self, mock_membership, mock_card_find, mock_user_get, mock_deltas
    ):
        """TC-2.A1.1: нема віртуальних транзакцій → effective_balance == balance."""
        card_id = "707f1f77bcf86cd799439044"
        card = _build_card(card_id, Decimal("1500.50"))

        mock_membership.return_value = True
        mock_card_find.return_value = _mock_card_find_cursor([card])
        mock_user_get.return_value = _mock_owner()
        # Порожній словник — для жодної картки нема віртуальних транзакцій
        mock_deltas.return_value = {}

        res = client.get(f"/api/v1/bank-cards/group/{GROUP_ID}")

        assert res.status_code == 200
        body = res.json()
        assert Decimal(body[0]["balance"]) == Decimal("1500.50")
        assert Decimal(body[0]["effective_balance"]) == Decimal("1500.50")

    @patch("app.api.bank_card.BankCardRepository.get_virtual_deltas_by_card_ids", new_callable=AsyncMock)
    @patch("app.api.bank_card.User.get", new_callable=AsyncMock)
    @patch("app.api.bank_card.BankCard.find")
    @patch("app.api.bank_card.GroupMembership.find_one", new_callable=AsyncMock)
    def test_tc_2_a2_1_only_credits_increase_effective(
        self, mock_membership, mock_card_find, mock_user_get, mock_deltas
    ):
        """TC-2.A2.1: лише кредити → effective_balance > balance."""
        card_id = "707f1f77bcf86cd799439055"
        card = _build_card(card_id, Decimal("500"))

        mock_membership.return_value = True
        mock_card_find.return_value = _mock_card_find_cursor([card])
        mock_user_get.return_value = _mock_owner()
        mock_deltas.return_value = {card_id: Decimal("200")}

        res = client.get(f"/api/v1/bank-cards/group/{GROUP_ID}")

        assert res.status_code == 200
        body = res.json()
        assert Decimal(body[0]["effective_balance"]) == Decimal("700")
        assert Decimal(body[0]["effective_balance"]) > Decimal(body[0]["balance"])

    @patch("app.api.bank_card.BankCardRepository.get_virtual_deltas_by_card_ids", new_callable=AsyncMock)
    @patch("app.api.bank_card.User.get", new_callable=AsyncMock)
    @patch("app.api.bank_card.BankCard.find")
    @patch("app.api.bank_card.GroupMembership.find_one", new_callable=AsyncMock)
    def test_tc_2_a3_1_only_debits_decrease_effective(
        self, mock_membership, mock_card_find, mock_user_get, mock_deltas
    ):
        """TC-2.A3.1: лише дебети → effective_balance < balance."""
        card_id = "707f1f77bcf86cd799439066"
        card = _build_card(card_id, Decimal("1000"))

        mock_membership.return_value = True
        mock_card_find.return_value = _mock_card_find_cursor([card])
        mock_user_get.return_value = _mock_owner()
        mock_deltas.return_value = {card_id: Decimal("-300")}

        res = client.get(f"/api/v1/bank-cards/group/{GROUP_ID}")

        assert res.status_code == 200
        body = res.json()
        assert Decimal(body[0]["effective_balance"]) == Decimal("700")
        assert Decimal(body[0]["effective_balance"]) < Decimal(body[0]["balance"])

    @patch("app.api.bank_card.BankCardRepository.get_virtual_deltas_by_card_ids", new_callable=AsyncMock)
    @patch("app.api.bank_card.User.get", new_callable=AsyncMock)
    @patch("app.api.bank_card.BankCard.find")
    @patch("app.api.bank_card.GroupMembership.find_one", new_callable=AsyncMock)
    def test_tc_2_a4_1_mixed_credits_and_debits_net_to_delta(
        self, mock_membership, mock_card_find, mock_user_get, mock_deltas
    ):
        """TC-2.A4.1: змішані кредити/дебети — репозиторій повертає суму (нетто)."""
        card_id = "707f1f77bcf86cd799439077"
        card = _build_card(card_id, Decimal("1000"))

        mock_membership.return_value = True
        mock_card_find.return_value = _mock_card_find_cursor([card])
        mock_user_get.return_value = _mock_owner()
        # Нетто з +500, +200, -300, -50 = +350
        mock_deltas.return_value = {card_id: Decimal("350")}

        res = client.get(f"/api/v1/bank-cards/group/{GROUP_ID}")

        assert res.status_code == 200
        body = res.json()
        assert Decimal(body[0]["effective_balance"]) == Decimal("1350")

    @patch("app.api.bank_card.BankCardRepository.get_virtual_deltas_by_card_ids", new_callable=AsyncMock)
    @patch("app.api.bank_card.User.get", new_callable=AsyncMock)
    @patch("app.api.bank_card.BankCard.find")
    @patch("app.api.bank_card.GroupMembership.find_one", new_callable=AsyncMock)
    def test_tc_2_ec2_1_zero_balance_with_positive_delta(
        self, mock_membership, mock_card_find, mock_user_get, mock_deltas
    ):
        """TC-2.EC2.1: raw balance=0, delta=+500 → effective_balance=500."""
        card_id = "707f1f77bcf86cd799439088"
        card = _build_card(card_id, Decimal("0"))

        mock_membership.return_value = True
        mock_card_find.return_value = _mock_card_find_cursor([card])
        mock_user_get.return_value = _mock_owner()
        mock_deltas.return_value = {card_id: Decimal("500")}

        res = client.get(f"/api/v1/bank-cards/group/{GROUP_ID}")

        assert res.status_code == 200
        body = res.json()
        assert Decimal(body[0]["balance"]) == Decimal("0")
        assert Decimal(body[0]["effective_balance"]) == Decimal("500")


class TestErrorPaths:
    """Тести помилкових сценаріїв 401/403/400."""

    @patch("app.api.bank_card.GroupMembership.find_one", new_callable=AsyncMock)
    def test_tc_2_e2_1_user_not_in_group_returns_403(self, mock_membership):
        """TC-2.E2.1: користувач не у групі → 403 Forbidden."""
        mock_membership.return_value = None

        res = client.get(f"/api/v1/bank-cards/group/{GROUP_ID}")

        assert res.status_code == 403

    def test_tc_2_e3_1_invalid_group_id_returns_400(self):
        """TC-2.E3.1: некоректний формат group_id → 400 Bad Request."""
        res = client.get("/api/v1/bank-cards/group/not-an-object-id")

        assert res.status_code == 400


class TestUnauthenticated:
    """TC-2.E1.1: 401 для неавторизованих запитів (без JWT)."""

    def test_tc_2_e1_1_unauthenticated_returns_401_or_403(self):
        """
        TC-2.E1.1: без JWT-токена ендпоінт має повертати 401/403.

        Тимчасово знімаємо override get_current_user, щоб реальна dependency
        обробила запит без Authorization-заголовка. HTTPBearer повертає 403
        у випадку відсутньго заголовка (це поведінка FastAPI за замовчуванням
        для HTTPBearer), тож приймаємо обидва коди як коректний негативний
        результат.
        """
        original_override = app.dependency_overrides.pop(get_current_user, None)
        try:
            res = client.get(f"/api/v1/bank-cards/group/{GROUP_ID}")
            assert res.status_code in (401, 403)
        finally:
            if original_override is not None:
                app.dependency_overrides[get_current_user] = original_override
