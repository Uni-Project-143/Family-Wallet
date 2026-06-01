"""
Unit-тести для схем TransferRequest / TransferResponse (UC-1, UC-6, UC-9, UC-10).

Покриває:
- TC-M.5..M.14: валідація суми, decimal_places, same-card, опціональні поля,
  довжина опису, успішна побудова TransferResponse.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.transaction import TransferRequest, TransferResponse


# ════════════════════════════════════════════════════════════════════════════
# TransferRequest — успішні сценарії
# ════════════════════════════════════════════════════════════════════════════


class TestTransferRequestValid:
    def test_tc_m5_valid_minimal_request(self):
        """TC-M.5: валідний TransferRequest з мінімальними полями будується."""
        req = TransferRequest(
            from_card_id="A",
            to_card_id="B",
            amount=Decimal("10.00"),
        )
        assert req.from_card_id == "A"
        assert req.to_card_id == "B"
        assert req.amount == Decimal("10.00")

    def test_tc_m9_amount_no_fractional_part_ok(self):
        """TC-M.9: amount=10 без дробової частини дозволено (decimal_places=2 — це 'до 2', не 'рівно 2')."""
        req = TransferRequest(
            from_card_id="A",
            to_card_id="B",
            amount=Decimal("10"),
        )
        assert req.amount == Decimal("10")

    def test_tc_m13_description_and_category_none_accepted(self):
        """TC-M.13: description=None та category_id=None приймаються (Optional defaults)."""
        req = TransferRequest(
            from_card_id="A",
            to_card_id="B",
            amount=Decimal("10.00"),
            description=None,
            category_id=None,
        )
        assert req.description is None
        assert req.category_id is None


# ════════════════════════════════════════════════════════════════════════════
# TransferRequest — невалідні сценарії
# ════════════════════════════════════════════════════════════════════════════


class TestTransferRequestInvalid:
    def test_tc_m6_amount_zero_rejected(self):
        """TC-M.6: amount=0 порушує gt=0."""
        with pytest.raises(ValidationError):
            TransferRequest(
                from_card_id="A",
                to_card_id="B",
                amount=Decimal("0"),
            )

    def test_tc_m7_amount_negative_rejected(self):
        """TC-M.7: amount=-1 порушує gt=0."""
        with pytest.raises(ValidationError):
            TransferRequest(
                from_card_id="A",
                to_card_id="B",
                amount=Decimal("-1"),
            )

    def test_tc_m8_amount_three_decimal_places_rejected(self):
        """TC-M.8: amount=10.123 порушує decimal_places=2."""
        with pytest.raises(ValidationError):
            TransferRequest(
                from_card_id="A",
                to_card_id="B",
                amount=Decimal("10.123"),
            )

    def test_tc_m10_missing_amount_rejected(self):
        """TC-M.10: відсутність amount є обов'язковим полем."""
        with pytest.raises(ValidationError):
            TransferRequest(
                from_card_id="A",
                to_card_id="B",
            )

    def test_tc_m11_same_card_rejected(self):
        """TC-M.11: from_card_id == to_card_id порушує model_validator."""
        with pytest.raises(ValidationError):
            TransferRequest(
                from_card_id="X",
                to_card_id="X",
                amount=Decimal("10.00"),
            )

    def test_tc_m12_description_too_long_rejected(self):
        """TC-M.12: description >500 символів порушує max_length."""
        with pytest.raises(ValidationError):
            TransferRequest(
                from_card_id="A",
                to_card_id="B",
                amount=Decimal("10.00"),
                description="x" * 501,
            )


# ════════════════════════════════════════════════════════════════════════════
# TransferResponse — успішна побудова
# ════════════════════════════════════════════════════════════════════════════


class TestTransferResponse:
    def test_tc_m14_constructs_with_all_fields(self):
        """TC-M.14: TransferResponse будується з усіма обов'язковими полями."""
        resp = TransferResponse(
            transfer_id="t",
            debit_transaction_id="d",
            credit_transaction_id="c",
            amount=Decimal("10"),
            from_effective_balance=Decimal("90"),
            to_effective_balance=Decimal("110"),
        )
        assert resp.transfer_id == "t"
        assert resp.debit_transaction_id == "d"
        assert resp.credit_transaction_id == "c"
        assert resp.amount == Decimal("10")
        assert resp.from_effective_balance == Decimal("90")
        assert resp.to_effective_balance == Decimal("110")
