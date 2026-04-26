from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from bson import ObjectId

from app.core.security import SECRET_KEY, ALGORITHM
from app.models.user import User

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    Розшифровує JWT токен і повертає поточного користувача з БД.
    Токен тепер містить лише userId.
    """
    token = credentials.credentials
    try:
        # Розшифровуємо токен
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("userId")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid token")

    # Перевіряємо валідність ObjectId, щоб сервер не впав із 500 помилкою
    try:
        user_obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid user ID format")

    # Шукаємо користувача в базі
    user = await User.get(user_obj_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User not found")

    return user

