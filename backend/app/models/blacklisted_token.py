from datetime import datetime
from beanie import Document
from pydantic import Field
import pymongo # Додаємо цей імпорт для створення індексу

class BlacklistedToken(Document):
    token: str
    added_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "blacklisted_tokens"
        # НОВЕ: Кажемо базі видаляти запис через певний час (наприклад, 7 днів = 604800 секунд)
        # Час треба ставити такий самий, як час життя твого JWT токена!
        indexes = [
            pymongo.IndexModel(
                [("added_at", pymongo.ASCENDING)],
                expireAfterSeconds=604800
            )
        ]
