import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from typing import Optional
import os


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Секретний ключ для JWT. У проді МАЄ бути заданий через env JWT_SECRET.
SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-key-for-development-only")
if os.getenv("ENV", "development").lower() == "production" and SECRET_KEY == "super-secret-key-for-development-only":
    raise RuntimeError("JWT_SECRET must be set in production environment.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 48


def verify_password(plain_password, hashed_password):
    """Перевіряє, чи збігається введений пароль із хешем у БД."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Генерує хеш для нового пароля."""
    return pwd_context.hash(password)


def create_access_token(user_id: str):
    """Створює JWT токен, який містить лише ID користувача."""
    expire = datetime.utcnow() + timedelta(hours=48)  # Або твій час

    # В payload тепер тільки userId та час життя
    payload = {
        "userId": user_id,
        "exp": expire
    }

    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
