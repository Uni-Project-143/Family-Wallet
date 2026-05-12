from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter

# Імпортуємо налаштування та обробники
from app.middleware.logging import log_requests_middleware
from app.exceptions import global_exception_handler, http_exception_handler

# Імпортуємо функцію ініціалізації БД
from app.config.database import init_db

# Імпортуємо наші актуальні роутери
from app.api import health, auth, group
from app.api import monobank
from app.api import transaction
from app.api.bank_card import bank_card_router

# ==========================================
# Менеджер життєвого циклу (Lifespan)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Ініціалізація підключення до MongoDB...")
    await init_db()
    print("База даних успішно підключена та моделі зареєстровані!")
    yield
    # (Тут код, який виконується при вимкненні сервера)

# ==========================================
# Ініціалізація додатку
# ==========================================
app = FastAPI(
    title="Family Wallet API",
    version="1.0.0",
    lifespan=lifespan
)

# Налаштування CORS (це потрібно для фронтенду)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 1. Підключаємо наше системне логування подій
app.add_middleware(BaseHTTPMiddleware, dispatch=log_requests_middleware)

# 2. Підключаємо централізовані обробники помилок
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

# 3. Підключаємо наші контролери (Роутери)
app.include_router(health.router)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(group.router, prefix="/api/v1/group", tags=["Group"])
app.include_router(transaction.router, prefix="/api/v1/transactions", tags=["Transactions"])
app.include_router(bank_card_router)

app.include_router(monobank.router)
