"""
Unit-тести для _extract_token_from_link з app/api/groups.py

Реальна поведінка функції:
- повертає токен (str) якщо посилання валідне
- кидає HTTPException(400) в усіх невалідних випадках
"""

import pytest
from fastapi import HTTPException

from app.api.groups import _extract_token_from_link


class TestExtractTokenFromLink:
    # ── Happy path ────────────────────────────────────────────────────────

    def test_valid_link_returns_token(self):
        url = "https://family-wallet.com/join/abc123xyz"
        assert _extract_token_from_link(url) == "abc123xyz"

    def test_valid_link_with_hex_token(self):
        """uuid4().hex — саме такий токен генерує InviteToken."""
        token = "a3f1c2d4e5b6a7f8c9d0e1f2a3b4c5d6"
        url = f"https://family-wallet.com/join/{token}"
        assert _extract_token_from_link(url) == token

    def test_valid_link_with_extra_path_prefix(self):
        """Шлях /app/join/<token> — parts[-2] == 'join' все одно."""
        url = "https://family-wallet.com/app/join/tok789"
        assert _extract_token_from_link(url) == "tok789"

    def test_valid_link_with_query_string_ignores_query(self):
        """Query string не впливає на токен."""
        url = "https://family-wallet.com/join/tok789?ref=email"
        assert _extract_token_from_link(url) == "tok789"

    # ── Negative: кидає HTTPException(400) ───────────────────────────────

    def test_link_without_join_segment_raises_400(self):
        with pytest.raises(HTTPException) as exc_info:
            _extract_token_from_link("https://family-wallet.com/groups/abc123")
        assert exc_info.value.status_code == 400

    def test_empty_token_after_join_raises_400(self):
        """Шлях /join/ без токена → parts[-1] == '' після split."""
        with pytest.raises(HTTPException) as exc_info:
            _extract_token_from_link("https://family-wallet.com/join/")
        assert exc_info.value.status_code == 400

    def test_only_join_no_token_raises_400(self):
        with pytest.raises(HTTPException) as exc_info:
            _extract_token_from_link("https://family-wallet.com/join")
        assert exc_info.value.status_code == 400

    def test_empty_string_raises_400(self):
        with pytest.raises(HTTPException) as exc_info:
            _extract_token_from_link("")
        assert exc_info.value.status_code == 400

    def test_random_string_no_join_raises_400(self):
        with pytest.raises(HTTPException) as exc_info:
            _extract_token_from_link("not-a-url-at-all")
        assert exc_info.value.status_code == 400

    def test_join_not_second_to_last_raises_400(self):
        """join є в шляху, але не перед токеном."""
        with pytest.raises(HTTPException) as exc_info:
            _extract_token_from_link("https://family-wallet.com/join/sub/token")
        assert exc_info.value.status_code == 400
