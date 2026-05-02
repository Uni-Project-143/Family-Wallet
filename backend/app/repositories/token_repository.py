from app.models.blacklisted_token import BlacklistedToken


class TokenRepository:

    @staticmethod
    async def add_to_blacklist(token: str):
        """Додає токен до чорного списку в БД."""
        new_token = BlacklistedToken(token=token)
        await new_token.insert()

    @staticmethod
    async def is_blacklisted(token: str) -> bool:
        """Перевіряє, чи є токен у чорному списку."""
        token_in_db = await BlacklistedToken.find_one(BlacklistedToken.token == token)
        return token_in_db is not None
