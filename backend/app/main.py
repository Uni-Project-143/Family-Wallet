import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.limiter import limiter
from app.middleware.logging import log_requests_middleware
from app.exceptions import global_exception_handler, http_exception_handler
from app.config.database import init_db

from app.api import health, auth, group
from app.api import monobank
from app.api import transaction
from app.api.bank_card import bank_card_router
from app.api.feed import router as feed_router
from app.api.ws import router as ws_router
from app.api.gift import router as gift_router
from app.services.gift_service import GiftService
from app.api.auth import router as auth_router
from app.api.request import router as requests_router


# ==========================================
# Менеджер життєвого циклу (Lifespan)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Ініціалізація підключення до MongoDB...")
    await init_db()
    print("База даних успішно підключена та моделі зареєстровані!")

    cron_task = asyncio.create_task(GiftService.reveal_gifts_cron())
    print("Cron job для Secret Gift запущено!")

    try:
        yield
    finally:
        cron_task.cancel()
        try:
            await cron_task
        except (asyncio.CancelledError, Exception):
            pass


# ==========================================
# Ініціалізація додатку
# ==========================================
app = FastAPI(
    title="Family Wallet API",
    version="1.0.0",
    lifespan=lifespan
)

# ------------------------------------------
# CORS — список origins береться з env CORS_ORIGINS
# (через кому). За замовчуванням — продакшен-фронт + localhost для dev.
# ------------------------------------------
_default_origins = ",".join([
    "https://family-wallet.pages.dev",
    "http://localhost:5173",
    "http://localhost:4173",
])
_cors_origins_raw = os.getenv("CORS_ORIGINS", _default_origins)
allow_origins = [o.strip() for o in _cors_origins_raw.split(",") if o.strip()]
allow_origin_regex = os.getenv("CORS_ORIGIN_REGEX") or None

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex=allow_origin_regex,
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

app.include_router(feed_router)
app.include_router(monobank.router)

app.include_router(ws_router)

app.include_router(gift_router)

app.include_router(auth_router)

app.include_router(requests_router)
