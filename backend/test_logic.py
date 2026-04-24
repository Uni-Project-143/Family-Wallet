import pytest
from unittest.mock import MagicMock

# --- (Service Layer) ---

def calculate_balance(income_list, expense_list):
    """Рахує загальний баланс гаманця"""
    return sum(income_list) - sum(expense_list)


def validate_transaction(amount):
    """Перевіряє правильність введеної суми"""
    if not isinstance(amount, (int, float)):
        raise TypeError("Сума повинна бути числом")
    if amount <= 0:
        raise ValueError("Сума транзакції повинна бути більшою за нуль")
    return True


def get_category_limit_status(current_spent, limit):
    """Перевіряє, чи не перевищено ліміт по категорії"""
    if current_spent > limit:
        return "Overlimit"
    return "OK"


# --- UNIT-ТЕСТИ ---

# Група 1: Математичні розрахунки (Баланс)
def test_balance_standard():
    # Тест 1: Звичайний розрахунок
    assert calculate_balance([1000, 500], [200, 300]) == 1000


def test_balance_negative():
    # Тест 2: Коли витрати перевищують доходи
    assert calculate_balance([100], [500]) == -400


def test_balance_empty():
    # Тест 3: Робота з порожніми списками (захист від помилок команди)
    assert calculate_balance([], []) == 0


# Група 2: Валідація даних (Пошук багів у логіці вводу)
def test_validate_success():
    # Тест 4: Коректне число
    assert validate_transaction(50.5) is True


def test_validate_zero_error():
    # Тест 5: Перевірка на нуль (має викинути помилку)
    with pytest.raises(ValueError):
        validate_transaction(0)


def test_validate_negative_error():
    # Тест 6: Перевірка на від'ємне число
    with pytest.raises(ValueError):
        validate_transaction(-100)


def test_validate_type_error():
    # Тест 7: Перевірка на введення тексту замість цифр
    with pytest.raises(TypeError):
        validate_transaction("сто гривень")


# Група 3: Ліміти та статуси
def test_limit_ok():
    # Тест 8: Ліміт не перевищено
    assert get_category_limit_status(80, 100) == "OK"


def test_limit_exceeded():
    # Тест 9: Ліміт перевищено (баг, якщо поверне OK)
    assert get_category_limit_status(120, 100) == "Overlimit"


def test_limit_exact():
    # Тест 10: Витрати рівно в ліміт
    assert get_category_limit_status(100, 100) == "OK"


# Група 4: MOCKING (Заміна реальної бази даних)
def test_mock_db_get_balance(mocker):
    # Тест 11: Замінюємо функцію через patch (як і було в оригіналі)
    # Ми патчимо об'єкт всередині тесту, щоб імітувати поведінку БД
    mock_db = mocker.patch('unittest.mock.MagicMock', autospec=True)
    mock_db.get_user_balance.return_value = 5000

    result = mock_db.get_user_balance(1)
    assert result == 5000


def test_mock_db_save_transaction(mocker):
    # Тест 12: Перевірка, чи викликається метод збереження
    mock_db = mocker.Mock()
    mock_db.save(amount=100)

    mock_db.save.assert_called_once_with(amount=100)


def test_mock_external_api_error(mocker):
    # Тест 13: Імітуємо збій сервера (Mocking Side Effects)
    mock_api = mocker.Mock()
    mock_api.get_rate.side_effect = ConnectionError("Server Down")

    with pytest.raises(ConnectionError):
        mock_api.get_rate("USD")


def test_mock_user_auth(mocker):
    # Тест 14: Імітація успішної авторизації користувача Illia
    mock_auth = mocker.Mock()
    mock_auth.get_current_user.return_value = {"id": 1, "name": "Illia"}

    user = mock_auth.get_current_user()
    assert user["name"] == "Illia"


def test_mock_empty_db_query(mocker):
    # Тест 15: Що поверне Mock, якщо в базі немає транзакцій
    mock_query = mocker.Mock()
    mock_query.find_all.return_value = []

    assert len(mock_query.find_all()) == 0
