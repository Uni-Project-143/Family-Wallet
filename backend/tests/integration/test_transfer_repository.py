"""
Інтеграційні тести для TransactionRepository.create_paired_virtual_transactions
(UC-1 happy path, UC-14 rollback).

Покриває:
- TC-1.2: успішна вставка пари віртуальних транзакцій повертає (debit_id, credit_id).
- TC-14.1: помилка під час credit-leg insert піднімає виняток і логує CRITICAL.
- TC-14.2: помилка під час debit-leg insert піднімає виняток і логує CRITICAL.
"""

import logging
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from bson import ObjectId

# Глушимо Beanie collection lookup, аби можна було будувати Transaction без init_beanie().
from beanie.odm.documents import Document
patch.object(Document, "get_pymongo_collection", return_value=MagicMock()).start()

from app.models.transaction import Transaction  # noqa: E402
from app.repositories.transaction_repository import TransactionRepository  # noqa: E402


# ════════════════════════════════════════════════════════════════════════════
# Допоміжні класи для мокання async-контекстів сесії MongoDB
# ════════════════════════════════════════════════════════════════════════════


class _AsyncCM:
    """Простий async context manager, який повертає переданий inner."""

    def __init__(self, inner):
        self.inner = inner

    async def __aenter__(self):
        return self.inner

    async def __aexit__(self, exc_type, exc, tb):
        return False


def _mock_session():
    """
    Будує мок-сесію MongoDB:
      - session сам по собі (повертається з start_session)
      - session.start_transaction() повертає async context manager
    """
    session = MagicMock()
    session.start_transaction = MagicMock(return_value=_AsyncCM(MagicMock()))
    return session


def _patch_start_session(session):
    """
    Патчить db_client.start_session у модулі transaction_repository.
    db_client.start_session() — це звичайна async-функція, яка ПОВЕРТАЄ async CM
    (відтворюємо патерн `async with await db_client.start_session()`).
    """
    return patch(
        "app.repositories.transaction_repository.db_client.start_session",
        new=AsyncMock(return_value=_AsyncCM(session)),
    )


def _build_tx(card_id: str, amount: Decimal, transfer_id: str) -> Transaction:
    return Transaction(
        card_id=card_id,
        amount=amount,
        group_id="grp",
        is_virtual=True,
        transfer_id=transfer_id,
    )


# ════════════════════════════════════════════════════════════════════════════
# TC-1.2: happy path
# ════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_tc_1_2_happy_path_returns_pair_of_ids():
    """TC-1.2: обидва insert проходять — повертається кортеж ID у вигляді рядків."""
    debit = _build_tx("card-A", Decimal("-10.00"), "tr-1")
    credit = _build_tx("card-B", Decimal("10.00"), "tr-1")

    debit_id = ObjectId()
    credit_id = ObjectId()

    async def _fake_insert(self, session=None):
        # Імітуємо Beanie: insert привласнює документу _id
        if self.card_id == "card-A":
            self.id = debit_id
        else:
            self.id = credit_id
        return self

    session = _mock_session()

    with _patch_start_session(session), patch.object(
        Transaction, "insert", new=_fake_insert
    ):
        result = await TransactionRepository.create_paired_virtual_transactions(
            debit, credit
        )

    assert result == (str(debit_id), str(credit_id))
    # Перевіряємо, що транзакційний контекст саме починався
    session.start_transaction.assert_called_once()


# ════════════════════════════════════════════════════════════════════════════
# TC-14.1: помилка на credit-leg
# ════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_tc_14_1_rollback_on_credit_failure(caplog):
    """TC-14.1: credit insert падає → виняток пробрасується, у логах CRITICAL з transfer_id."""
    debit = _build_tx("card-A", Decimal("-10.00"), "tr-credit-fail")
    credit = _build_tx("card-B", Decimal("10.00"), "tr-credit-fail")

    debit_id = ObjectId()

    async def _fake_insert(self, session=None):
        if self.card_id == "card-A":
            self.id = debit_id
            return self
        raise Exception("credit failed")

    session = _mock_session()

    with caplog.at_level(logging.CRITICAL, logger="app.repositories.transaction_repository"):
        with _patch_start_session(session), patch.object(
            Transaction, "insert", new=_fake_insert
        ):
            with pytest.raises(Exception, match="credit failed"):
                await TransactionRepository.create_paired_virtual_transactions(
                    debit, credit
                )

    critical_records = [r for r in caplog.records if r.levelno == logging.CRITICAL]
    assert critical_records, "Очікувався CRITICAL-запис у логах при відкаті."
    record = critical_records[0]
    assert record.message == "TRANSFER_ROLLBACK_FAILED"
    assert getattr(record, "transfer_id", None) == "tr-credit-fail"
    assert getattr(record, "debit_card_id", None) == "card-A"
    assert getattr(record, "credit_card_id", None) == "card-B"


# ════════════════════════════════════════════════════════════════════════════
# TC-14.2: помилка на debit-leg
# ════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_tc_14_2_rollback_on_debit_failure(caplog):
    """TC-14.2: debit insert падає → виняток пробрасується, у логах CRITICAL."""
    debit = _build_tx("card-A", Decimal("-10.00"), "tr-debit-fail")
    credit = _build_tx("card-B", Decimal("10.00"), "tr-debit-fail")

    async def _fake_insert(self, session=None):
        raise Exception("debit failed")

    session = _mock_session()

    with caplog.at_level(logging.CRITICAL, logger="app.repositories.transaction_repository"):
        with _patch_start_session(session), patch.object(
            Transaction, "insert", new=_fake_insert
        ):
            with pytest.raises(Exception, match="debit failed"):
                await TransactionRepository.create_paired_virtual_transactions(
                    debit, credit
                )

    critical_records = [r for r in caplog.records if r.levelno == logging.CRITICAL]
    assert critical_records, "Очікувався CRITICAL-запис у логах при відкаті."
    record = critical_records[0]
    assert record.message == "TRANSFER_ROLLBACK_FAILED"
    assert getattr(record, "transfer_id", None) == "tr-debit-fail"
