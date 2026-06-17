import httpx
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

class MonobankClient:
    BASE_URL = "https://api.monobank.ua"

    @classmethod
    async def get_client_info(cls, personal_token: str) -> dict:
        headers = {"X-Token": personal_token}
        timeout = httpx.Timeout(10.0)

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.get(f"{cls.BASE_URL}/personal/client-info", headers=headers)

                if response.status_code == 403:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid Monobank token"
                    )

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                logger.error(f"Monobank API error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Monobank API is currently unavailable. Please try again later."
                )
            except httpx.RequestError as e:
                logger.error(f"Monobank API connection failed: {e}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Please try again later."
                )

    @classmethod
    async def register_webhook(cls, personal_token: str, webhook_url: str) -> bool:
        headers = {"X-Token": personal_token}
        payload = {"webHookUrl": webhook_url}
        timeout = httpx.Timeout(10.0)

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.post(
                    f"{cls.BASE_URL}/personal/webhook",
                    headers=headers,
                    json=payload
                )

                if response.status_code == 403:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid Monobank token"
                    )

                response.raise_for_status()
                return True

            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                logger.error(f"Monobank webhook registration error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Failed to register Monobank webhook."
                )
