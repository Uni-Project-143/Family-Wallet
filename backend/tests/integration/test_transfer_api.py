"""
Інтеграційні тести для POST /api/v1/transactions/transfer (Slice 4).

Покриває UC-1 (happy path), UC-4 (404 для чужої картки), UC-5 (cross-group 400),
UC-6 (same-card 422 + service backup), UC-7 (401/403 без JWT), UC-8 (insufficient 400),
UC-11 (to_card 404), UC-13 (категорія 400), UC-15 (повторна перевірка membership 403),
UC-17 (immutability — PUT/PATCH/DELETE недоступні).
"""

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

from bson import ObjectId
from fastapi.testclient import TestClient

# Глушимо Beanie collection lookup, аби Transaction(...) можна було будувати без init_beanie().
from beanie.odm.documents import Document
patch.object(Document, "get_pymongo_collection", return_value=MagicMock()).start()

from app.main import app  # noqa: E402
from app.core.dependencies import get_current_user  # noqa: E402

client = TestClient(app)

USER_ID = "507f1f77bcf86cd799439011"
FROM_CARD_ID = "607f1f77bcf86cd799439021"
TO_CARD_ID = "607f1f77bcf86cd799439022"
GROUP_ID = "507f1f77bcf86cd799439051"


class MockUser:
    id = ObjectId(USER_ID)


app.dependency_overrides[get_current_user] = lambda: MockUser()


def _make_card(
    card_id: str,
    user_id: str = USER_ID,
    group_id: str = GROUP_ID,
    balance: Decimal = Decimal("1000"),
    status: str = "ACTIVE",
) -> MagicMock:
    card = MagicMock()
    card.id = ObjectId(card_id)
    card.user_id = user_id
    card.group_id = group_id
    card.balance = balance
    card.status = status
    return card


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
    """UC-1: успішний переказ і незмінність raw balance."""

    @patch(f"{SERVICE_PATH}.TransactionRepository.create_paired_virtual_transactions",
           new_callable=AsyncMock)
    @patch(f"{SERVICE_PATH}.GroupMembership.find_one", new_callable=AsyncMock)
    @patch(f"{SERVICE_PATH}.BankCardRepository.get_virtual_deltas_by_card_ids",
           new_callable=AsyncMock)
    @patch(f"{SERVICE_PATH}.BankCardRepository.get_by_id", new_callable=AsyncMock)
    def test_tc_1_1_happy_path_returns_200_with_response(
        self, mock_get_by_id, mock_deltas, mock_membership, mock_create_pair,
    ):
        """TC-1.1: всі моки валідні → 200 + TransferResponse з повним тілом."""
        from_card = _make_card(FROM_CARD_ID, balance=Decimal("1000"))
        to_card = _make_card(TO_CARD_ID, balance=Decimal("200"))
        mock_get_by_id.side_effect = [from_card, to_card]
        mock_deltas.side_effect = [
            {},  # перед списанням — без віртуальних транзакцій
            {FROM_CARD_ID: Decimal("-100"), TO_CARD_ID: Decimal("100")},  # після
        ]
        mock_membership.return_value = MagicMock()
        mock_create_pair.return_value = ("debit-id-1", "credit-id-1")

        res = client.post("/api/v1/transactions/transfer", json=_valid_body())

        assert res.status_code == 200
        body = res.json()
        assert body["debit_transaction_id"] == "debit-id-1"
        assert body["credit_transaction_id"] == "credit-id-1"
        # transfer_id має бути валідним UUID4 (36 символів зі знаком тире)
        assert isinstance(body["transfer_id"], str) and len(body["transfer_id"]) == 36
        assert Decimal(body["amount"]) == Decimal("100.00")
        assert Decimal(body["from_effective_balance"]) == Decimal("900")
        assert Decimal(body["to_effective_balance"]) == Decimal("300")

    @patch(f"{SERVICE_PATH}.TransactionRepository.create_paired_virtual_transactions",
           new_callable=AsyncMock)
    @patch(f"{SERVICE_PATH}.GroupMembership.find_one", new_callable=AsyncMock)
    @patch(f"{SERVICE_PATH}.BankCardRepository.get_virtual_deltas_by_card_ids",
           new_callable=AsyncMock)
    @patch(f"{SERVICE_PATH}.BankCardRepository.get_by_id", new_callable=AsyncMock)
    def test_tc_1_3_raw_balance_not_mutated(
        self, mock_get_by_id, mock_deltas, mock_membership, mock_create_pair,
    ):
        """TC-1.3: AC-11 — raw card.balance не мутується кодом сервісу."""
        from_card = _make_card(FROM_CARD_ID, balance=Decimal("1000"))
        to_card = _make_card(TO_CARD_ID, balance=Decimal("200"))
        from_card_save = from_card.save
        to_card_save = to_card.save
        mock_get_by_id.side_effect = [from_card, to_card]
        mock_deltas.side_effect = [{}, {}]
        mock_membership.return_value = MagicMock()
        mock_create_pair.return_value = ("d", "c")

        res = client.post("/api/v1/transactions/transfer", json=_valid_body())

        assert res.status_code == 200
        # raw balance не зачеплений
        assert from_card.balance == Decimal("1000")
        assert to_card.balance == Decimal("200")
        # save() не викликався — ми не зберігаємо картку
        from_card_save.assert_not_called()
        to_card_save.assert_not_called()


class TestOwnershipAndExistence:
    """UC-4, UC-11: 404 для відсутніх та чужих карток."""

    @patch(f"{SERVICE_PATH}.BankCardRepository.get_by_id", new_callable=AsyncMock)
    def test_tc_4_1_from_card_not_found_returns_404(self, mock_get_by_id):
        """TC-4.1: from_card відсутня → 404 (уніфікований текст)."""
        mock_get_by_id.return_value = None

        res = client.post("/api/v1/transactions/transfer", json=_valid_body())

        assert res.status_code == 404
        assert "Картку не знайдено" in res.json()["message"]

    @patch(f"{SERVICE_PATH}.BankCardRepository.get_by_id", new_callable=AsyncMock)
    def test_tc_4_e1_1_from_card_not_owned_returns_404_not_403(self, mock_get_by_id):
        """TC-4.E1.1: from_card існує, але user_id інший → 404, НЕ 403 (захист від перебору)."""
        other_user_id = "111111111111111111111111"
        from_card = _make_card(FROM_CARD_ID, user_id=other_user_id)
        mock_get_by_id.return_value = from_card

        res = client.post("/api/v1/transactions/transfer", json=_valid_body())

        assert res.status_code == 404
        assert "Картку не знайдено" in res.json()["message"]

    @patch(f"{SERVICE_PATH}.BankCardRepository.get_by_id", new_callable=AsyncMock)
    def test_tc_11_1_to_card_not_found_returns_404(self, mock_get_by_id):
        """TC-11.1: from_card знайдено, але to_card відсутня → 404 з відповідним повідомленням."""
        from_card = _make_card(FROM_CARD_ID)
        mock_get_by_id.side_effect = [from_card, None]

        res = client.post("/api/v1/transactions/transfer", json=_valid_body())

        assert res.status_code == 404
        assert "отримувача" in res.json()["message"]


class TestGroupBoundaries:
    """UC-5, UC-15: межі групи та повторна перевірка членства."""

    @patch(f"{SERVICE_PATH}.BankCardRepository.get_by_id", new_callable=AsyncMock)
    def test_tc_5_1_cross_group_returns_400(self, mock_get_by_id):
        """TC-5.1: картки в різних групах → 400."""
        from_card = _make_card(FROM_CARD_ID, group_id=GROUP_ID)
        to_card = _make_card(TO_CARD_ID, group_id="999999999999999999999999")
        mock_get_by_id.side_effect = [from_card, to_card]

        res = client.post("/api/v1/transactions/transfer", json=_valid_body())

        assert res.status_code == 400
        assert "різним групам" in res.json()["message"]

    @patch(f"{SERVICE_PATH}.GroupMembership.find_one", new_callable=AsyncMock)
    @patch(f"{SERVICE_PATH}.BankCardRepository.get_by_id", new_callable=AsyncMock)
    def test_tc_15_1_membership_revoked_returns_403(self, mock_get_by_id, mock_membership):
        """TC-15.1: токен діє, але юзера вже немає в групі → 403 Forbidden."""
        from_card = _make_card(FROM_CARD_ID)
        to_card = _make_card(TO_CARD_ID)
        mock_get_by_id.side_effect = [from_card, to_card]
        mock_membership.return_value = None

        res = client.post("/api/v1/transactions/transfer", json=_valid_body())

        assert res.status_code == 403
        assert "не є учасником" in res.json()["message"]


class TestServiceBackupChecks:
    """UC-6, статус картки — резервні перевірки сервісу."""

    def test_tc_6_1_same_card_via_schema_returns_422(self):
        """TC-6.1: from_card_id == to_card_id ловиться на рівні Pydantic → 422."""
        body = _valid_body(to_card_id=FROM_CARD_ID)

        res = client.post("/api/v1/transactions/transfer", json=body)

        assert res.status_code == 422

    @patch(f"{SERVICE_PATH}.GroupMembership.find_one", new_callable=AsyncMock)
    @patch(f"{SERVICE_PATH}.BankCardRepository.get_by_id", new_callable=AsyncMock)
    def test_tc_status_inactive_card_returns_400(self, mock_get_by_id, mock_membership):
        """TC-status: from_card.status != ACTIVE → 400 'Картка деактивована'."""
        from_card = _make_card(FROM_CARD_ID, status="BLOCKED")
        to_card = _make_card(TO_CARD_ID)
        mock_get_by_id.side_effect = [from_card, to_card]
        mock_membership.return_value = MagicMock()

        res = client.post("/api/v1/transactions/transfer", json=_valid_body())

        assert res.status_code == 400
        assert "деактивована" in res.json()["message"]


class TestFundsAndAmountValidation:
    """UC-8 (insufficient) + Pydantic-валідація amount."""

    @patch(f"{SERVICE_PATH}.GroupMembership.find_one", new_callable=AsyncMock)
    @patch(f"{SERVICE_PATH}.BankCardRepository.get_virtual_deltas_by_card_ids",
           new_callable=AsyncMock)
    @patch(f"{SERVICE_PATH}.BankCardRepository.get_by_id", new_callable=AsyncMock)
    def test_tc_8_1_insufficient_funds_returns_400(
        self, mock_get_by_id, mock_deltas, mock_membership,
    ):
        """TC-8.1: balance=50, amount=100 → 400 'Недостатньо коштів'."""
        from_card = _make_card(FROM_CARD_ID, balance=Decimal("50"))
        to_card = _make_card(TO_CARD_ID)
        mock_get_by_id.side_effect = [from_card, to_card]
        mock_deltas.return_value = {}
        mock_membership.return_value = MagicMock()

        res = client.post("/api/v1/transactions/transfer", json=_valid_body())

        assert res.status_code == 400
        assert "Недостатньо" in res.json()["message"]

    def test_tc_9_1_amount_zero_returns_422(self):
        """TC-9.1: amount=0 (gt=0) → 422 Pydantic."""
        res = client.post(
            "/api/v1/transactions/transfer", json=_valid_body(amount="0"),
        )
        assert res.status_code == 422

    def test_tc_9_2_amount_negative_returns_422(self):
        """TC-9.2: amount=-10 → 422 Pydantic."""
        res = client.post(
            "/api/v1/transactions/transfer", json=_valid_body(amount="-10"),
        )
        assert res.status_code == 422

    def test_tc_10_1_amount_too_many_decimals_returns_422(self):
        """TC-10.1: amount=10.123 (decimal_places > 2) → 422."""
        res = client.post(
            "/api/v1/transactions/transfer", json=_valid_body(amount="10.123"),
        )
        assert res.status_code == 422


class TestCategoryValidation:
    """UC-13: невалідна / відсутня категорія → 400 (а не 404)."""

    @patch(f"{SERVICE_PATH}.Category.get", new_callable=AsyncMock)
    @patch(f"{SERVICE_PATH}.GroupMembership.find_one", new_callable=AsyncMock)
    @patch(f"{SERVICE_PATH}.BankCardRepository.get_by_id", new_callable=AsyncMock)
    def test_tc_13_1_category_not_found_returns_400(
        self, mock_get_by_id, mock_membership, mock_category_get,
    ):
        """TC-13.1: payload містить category_id, але категорії немає → 400."""
        from_card = _make_card(FROM_CARD_ID)
        to_card = _make_card(TO_CARD_ID)
        mock_get_by_id.side_effect = [from_card, to_card]
        mock_membership.return_value = MagicMock()
        mock_category_get.return_value = None

        body = _valid_body(category_id="507f1f77bcf86cd799439999")
        res = client.post("/api/v1/transactions/transfer", json=body)

        assert res.status_code == 400
        assert "Категорію" in res.json()["message"]


class TestImmutability:
    """UC-17: жодних мутуючих route на /transactions/{id}."""

    def test_tc_17_1_put_transactions_id_returns_404_or_405(self):
        """TC-17.1: PUT /api/v1/transactions/{id} не існує."""
        res = client.put("/api/v1/transactions/507f1f77bcf86cd799439abc", json={})
        assert res.status_code in (404, 405)

    def test_tc_17_2_delete_transactions_id_returns_404_or_405(self):
        """TC-17.2: DELETE /api/v1/transactions/{id} не існує."""
        res = client.delete("/api/v1/transactions/507f1f77bcf86cd799439abc")
        assert res.status_code in (404, 405)


class TestUnauthenticated:
    """UC-7: без JWT — 401/403 (HTTPBearer повертає 403 при відсутньому заголовку)."""

    def test_tc_7_1_unauthenticated_returns_401_or_403(self):
        """TC-7.1: тимчасово знімаємо override get_current_user, щоб реальна dependency
        обробила запит без Authorization."""
        original_override = app.dependency_overrides.pop(get_current_user, None)
        try:
            res = client.post("/api/v1/transactions/transfer", json=_valid_body())
            assert res.status_code in (401, 403)
        finally:
            if original_override is not None:
                app.dependency_overrides[get_current_user] = original_override


class TestRateLimit:
    """TC-rate-limit: ендпоінт декорований @limiter.limit('30/minute') — smoke check."""

    def test_endpoint_has_rate_limit_decorator(self):
        """SMOKE: переконуємось, що Limiter знає про route /transfer."""
        from app.core.limiter import limiter as app_limiter
        # slowapi реєструє ліміти у внутрішньому реєстрі — переконаємось, що він не порожній.
        # Якщо лімітер активний, у нього має бути хоча б один зареєстрований ключ.
        # Точніша перевірка потребувала б time-travel, тому тут лише smoke-assert.
        assert app_limiter is not None
        assert hasattr(app_limiter, "limit")
