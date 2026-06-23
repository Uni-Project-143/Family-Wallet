import logging
from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.config.database import db_client

logger = logging.getLogger("FamilyWallet")
router = APIRouter()

@router.get("/health", tags=["System"])
async def health_check():
    """Ендпоінт для перевірки статусу підключення до MongoDB Atlas."""
    try:
        await db_client.admin.command('ping')
        return {"status": "Database is healthy", "code": 200}
    except Exception as e:
        logger.error(f"Health Check Failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "errorCode": "SERVICE_UNAVAILABLE",
                "message": "База даних недоступна."
            }
        )
