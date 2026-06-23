"""
Unit-тести для моделі Transaction та схеми TransactionResponse.

Покриває:
- TC-M.1..M.3: дефолти нових полів (is_virtual, transfer_id) та опціональність category_id
- TC-M.4: round-trip is_virtual / transfer_id (зворотна сумісність)
- TC-M.5: наявність нових індексів у Settings.indexes
- TC-M.6: дефолти TransactionResponse при мінімальних обов'язкових полях
"""

from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

# Чит-код з test_group_service.py: глушимо звертання до Mongo-колекції у ядрі Beanie,
# щоб юніт-тести не вимагали реального init_beanie().
from beanie.odm.documents import Document
patch.object(Document, "get_pymongo_collection", return_value=MagicMock()).start()

from app.models.transaction import Transaction  # noqa: E402
from app.schemas.transaction import TransactionResponse  # noqa: E402


# ════════════════════════════════════════════════════════════════════════════
# Дефолти полів моделі Transaction
# ════════════════════════════════════════════════════════════════════════════


class TestTransactionDefaults:
    def test_is_virtual_default_false(self):
        """TC-M.1: новостворена транзакція має is_virtual == False."""
        tx = Transaction(card_id="x", amount=Decimal("10"), group_id="g")
        assert tx.is_virtual is False

    def test_transfer_id_default_none(self):
        """TC-M.2: новостворена транзакція має transfer_id is None."""
        tx = Transaction(card_id="x", amount=Decimal("10"), group_id="g")
        assert tx.transfer_id is None

    def test_category_id_optional_default_none(self):
        """TC-M.3: category_id став Optional — без передачі дорівнює None."""
        tx = Transaction(card_id="x", amount=Decimal("10"), group_id="g")
        assert tx.category_id is None


# ════════════════════════════════════════════════════════════════════════════
# Round-trip нових полів (backward compat / forward compat)
# ════════════════════════════════════════════════════════════════════════════


class TestTransactionRoundTrip:
    def test_is_virtual_and_transfer_id_round_trip(self):
        """TC-M.4: явно передані is_virtual / transfer_id зберігаються коректно."""
        tx = Transaction(
            card_id="x",
            amount=Decimal("10"),
            group_id="g",
            is_virtual=True,
            transfer_id="abc",
        )
        assert tx.is_virtual is True
        assert tx.transfer_id == "abc"


# ════════════════════════════════════════════════════════════════════════════
# Індекси (NFR-04 + UC-3-A2 + UC-14)
# ════════════════════════════════════════════════════════════════════════════


def _index_keys(index_model):
    """Витягує список ключів індексу як список кортежів (name, direction)."""
    document = index_model.document
    key = document.get("key")
    if key is None:
        return []
    # У pymongo .document["key"] — це SON / dict {field: direction}
    return list(key.items())


def _index_is_sparse(index_model):
    return bool(index_model.document.get("sparse", False))


class TestTransactionIndexes:
    def test_card_id_is_virtual_compound_index_present(self):
        """TC-M.5 (частина 1): є складений індекс [(card_id, 1), (is_virtual, 1)]."""
        found = False
        for idx in Transaction.Settings.indexes:
            keys = _index_keys(idx)
            if keys == [("card_id", 1), ("is_virtual", 1)]:
                found = True
                break
        assert found, (
            "Очікувався складений індекс [(card_id, 1), (is_virtual, 1)] "
            "для агрегацій effective_balance (NFR-04)."
        )

    def test_transfer_id_sparse_index_present(self):
        """TC-M.5 (частина 2): є sparse індекс по transfer_id (не unique)."""
        found = False
        for idx in Transaction.Settings.indexes:
            keys = _index_keys(idx)
            if keys == [("transfer_id", 1)] and _index_is_sparse(idx):
                # Має бути саме sparse і саме НЕ unique
                assert not idx.document.get("unique", False), (
                    "transfer_id індекс повинен бути sparse, але НЕ unique "
                    "(дві ноги переказу мають однаковий transfer_id)."
                )
                found = True
                break
        assert found, "Очікувався sparse індекс по transfer_id."


# ════════════════════════════════════════════════════════════════════════════
# TransactionResponse — дефолти нових полів
# ════════════════════════════════════════════════════════════════════════════


class TestTransactionResponseDefaults:
    def test_minimal_construction_uses_defaults(self):
        """TC-M.6: TransactionResponse будується без is_virtual / transfer_id / category_id."""
        response = TransactionResponse(
            id="tx-1",
            card_id="card-1",
            amount=Decimal("100"),
            currency="UAH",
            timestamp=datetime(2026, 1, 1, 12, 0, 0),
        )
        assert response.category_id is None
        assert response.is_virtual is False
        assert response.transfer_id is None
        assert response.reactions == []
