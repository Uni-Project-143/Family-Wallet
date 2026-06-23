import logging
import time
from fastapi import Request

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("FamilyWallet")


async def log_requests_middleware(request: Request, call_next):
    """Фіксує кожен HTTP-запит (Метод, Шлях, Статус-код)."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    logger.info(
        f"Method: {request.method} | Path: {request.url.path} | "
        f"Status: {response.status_code} | Time: {process_time:.4f}s"
    )
    return response
