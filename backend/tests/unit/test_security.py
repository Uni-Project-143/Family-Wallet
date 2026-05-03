"""
Unit-тести для app/core/security.py

Покриває:
- get_password_hash + verify_password (bcrypt round-trip)
- create_access_token + ручне декодування JWT (userId, exp)
"""

import time
import jwt
import pytest

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
)


# ════════════════════════════════════════════════════════════════════════════
# get_password_hash + verify_password
# ════════════════════════════════════════════════════════════════════════════


class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        assert get_password_hash("secret") != "secret"

    def test_correct_password_verifies(self):
        password = "MyStr0ngP@ss"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_wrong_password_does_not_verify(self):
        hashed = get_password_hash("correct-password")
        assert verify_password("wrong-password", hashed) is False

    def test_empty_password_round_trip(self):
        hashed = get_password_hash("")
        assert verify_password("", hashed) is True
        assert verify_password("notempty", hashed) is False

    def test_two_hashes_of_same_password_differ(self):
        """bcrypt додає сіль — кожен хеш унікальний."""
        pw = "same-password"
        assert get_password_hash(pw) != get_password_hash(pw)


# ════════════════════════════════════════════════════════════════════════════
# create_access_token + декодування JWT
# ════════════════════════════════════════════════════════════════════════════


class TestCreateAccessToken:
    def test_token_contains_user_id(self):
        user_id = "507f1f77bcf86cd799439011"
        token = create_access_token(user_id)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # реальний код кладе "userId", не "sub"
        assert payload["userId"] == user_id

    def test_token_contains_exp(self):
        token = create_access_token("uid-001")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload
        assert payload["exp"] > int(time.time())

    def test_token_expires_in_roughly_48h(self):
        token = create_access_token("uid-002")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        seconds_left = payload["exp"] - int(time.time())
        # має бути між 23 і 25 годинами
        assert 47 * 3600 < seconds_left < 49 * 3600

    def test_expired_token_raises(self):
        """Перевіряємо, що PyJWT відхиляє протерміновані токени."""
        from datetime import datetime, timedelta

        payload = {
            "userId": "uid-003",
            "exp": datetime.utcnow() - timedelta(seconds=1),
        }
        expired_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(expired_token, SECRET_KEY, algorithms=[ALGORITHM])

    def test_wrong_secret_raises(self):
        token = create_access_token("uid-004")
        with pytest.raises(jwt.PyJWTError):
            jwt.decode(token, "wrong-secret", algorithms=[ALGORITHM])

    def test_token_is_string(self):
        """PyJWT 2.x повертає str, не bytes."""
        token = create_access_token("uid-005")
        assert isinstance(token, str)
