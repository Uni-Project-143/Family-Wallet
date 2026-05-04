import httpx
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class MonobankClient:
    BASE_URL = "https://api.monobank.ua"

    @classmethod
    async def get_client_info(cls, personal_token: str) -> dict:
        """
        BE-01: Валідація токена та отримання інформації про рахунки.
        """
        headers = {"X-Token": personal_token}
        timeout = httpx.Timeout(10.0)  # Захист від зависань Монобанку

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.get(f"{cls.BASE_URL}/personal/client-info", headers=headers)

                # AC: Невалідний токен (Monobank повертає 403) -> 400
                if response.status_code == 403:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Невірний токен Monobank"
                    )

                response.raise_for_status()  # Якщо статус 500 тощо, викине помилку
                return response.json()

            except httpx.HTTPStatusError as e:
                logger.error(f"Monobank API error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Monobank API зараз недоступний. Спробуйте пізніше."
                )
            except httpx.RequestError as e:
                logger.error(f"Monobank API connection failed: {e}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Спробуйте пізніше"  # AC: timeout -> 503
                )

    @classmethod
    async def register_webhook(cls, personal_token: str, webhook_url: str) -> bool:
        """
        BE-02: Реєстрація webhook URL у Monobank.
        """
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
                        detail="Невірний токен Monobank"
                    )

                response.raise_for_status()
                return True

            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                logger.error(f"Monobank webhook registration error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Не вдалося зареєструвати вебхук у Monobank."
                )
