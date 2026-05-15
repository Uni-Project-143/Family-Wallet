"""
conftest.py — спільна конфігурація для всього тестового suite.
"""

import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture(scope="session", autouse=True)
def disable_db_for_integration_tests(request):
    """
    Відключає підключення до бази ТІЛЬКИ для інтеграційних тестів.
    Юніт-тести потребують ініціалізованих моделей Beanie для перевірки атрибутів.
    """
    # Отримуємо шляхи всіх тестів, які зараз запускаються
    test_paths = [str(p.path) for p in request.session.items]

    # Якщо ми запускаємо ТІЛЬКИ юніт-тести (в шляху є папка 'unit')
    # Дозволяємо Beanie нормально зареєструвати моделі в пам'яті
    if all("unit" in path for path in test_paths):
        yield
        return

    # Інакше (якщо запускаємо інтеграційні тести або всі разом) - глушимо підключення
    with patch("app.config.database.AsyncIOMotorClient"):
        with patch("beanie.init_beanie", new_callable=AsyncMock):
            yield
