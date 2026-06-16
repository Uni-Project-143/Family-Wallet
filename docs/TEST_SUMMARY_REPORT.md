# Test Summary Report — Family Wallet

**Проєкт:** Family Wallet (веб-застосунок для управління сімейним бюджетом)
**Дата фінального тестування:** 16.06.2026
**Версія:** MVP (гілка `dev`)
**Статус:** Пройдено — 100% тест-кейсів успішні

---

## 1. Статистика тестування

| Показник                       | Значення        |
| ------------------------------ | --------------- |
| Загальна кількість тест-кейсів | **89**          |
| Успішних (passed)              | **89 (100%)**   |
| Невдалих (failed)              | 0               |
| Пропущених (skipped)           | 0               |
| Відкритих критичних дефектів   | 0               |

> Для MVP досягнуто цільового показника **100% успішних тестів**.

### Розподіл за типами

| Набір          | Кількість | Результат | Час виконання |
| -------------- | --------- |-----------| ------------- |
| Unit-тести     | 37        | passed    | ~15.2 с       |
| Integration    | 52        | passed    | ~8.0 с        |
| **Разом**      | **89**    | 100%      | —             |

### Деталізація за файлами

**Unit (37):**

| Файл                       | Тести |
| -------------------------- | ----- |
| `test_security.py`         | 11    |
| `test_transfer_schemas.py` | 10    |
| `test_transaction_model.py`| 7     |
| `test_group_service.py`    | 5     |
| `test_monobank_service.py` | 4     |

**Integration (52):**

| Файл                          | Тести |
| ----------------------------- | ----- |
| `test_transfer_api.py`        | 18    |
| `test_bank_card_api.py`       | 9     |
| `test_auth_api.py`            | 8     |
| `test_group_api.py`           | 5     |
| `test_feed_api.py`            | 3     |
| `test_transfer_repository.py` | 3     |
| `test_health.py`              | 2     |
| `test_monobank_api.py`        | 2     |
| `test_transaction_api.py`     | 2     |

---

## 2. Environment Info

Середовище, на якому проводився фінальний прогін тестів:

| Параметр              | Значення                                  |
| --------------------- | ----------------------------------------- |
| ОС                    | Windows (win32)                           |
| Python                | 3.13.2                                     |
| Test runner           | pytest 9.0.3, pluggy 1.6.0                 |
| Плагіни               | anyio 4.13.0, pytest-asyncio 1.3.0         |
| Режим asyncio         | auto                                       |
| База даних            | MongoDB Atlas (тестовий кластер)           |
| Спосіб запуску        | локальний `venv` + `pytest`                |

**Команди запуску:**

```bash
cd backend
# (одноразово) встановити залежності, включно з firebase-admin/sendgrid
pip install -r requirements.txt

pytest                    # усі тести
pytest tests/unit         # лише unit
pytest tests/integration  # лише integration
```

**Ручне тестування (фронтенд):** застосунок перевірявся через Docker Compose
(`docker-compose up --build`), backend на `http://localhost:8000`, frontend на
`http://localhost:5173`, у сучасному desktop-браузері (Chrome/Edge).

---

## 3. Known Issues (Transparency Policy)

Перелік відомих дрібних дефектів, **некритичних** для MVP:

1. **DeprecationWarning: `datetime.utcnow()`**
   Використовується у кількох модулях (`app/exceptions.py`, `app/api/health.py`,
   `app/core/security.py`, `app/services/group_service.py`, моделі). Метод
   застарів у Python 3.12+. На роботу не впливає; рекомендована міграція на
   `datetime.now(datetime.UTC)`.

2. **Pydantic deprecation warnings**
   Попередження про class-based `Config` та extra-аргументи у `Field(...)`
   (Pydantic V2). Функціональність коректна; варто перейти на `ConfigDict` і
   `json_schema_extra` перед оновленням до Pydantic V3.

3. **`InsecureKeyLengthWarning` у `test_security.py::test_wrong_secret_raises`**
   Тест свідомо використовує короткий HMAC-ключ (12 байт) для перевірки негативного
   сценарію. Стосується лише тестових даних, не продакшн-конфігурації.

4. **Прерквізити середовища для запуску тестів**
   - Integration-тести імпортують `app.main`, тому в `venv` мають бути встановлені
     `firebase-admin` та `sendgrid` (`pip install -r requirements.txt`). Без них
     збір integration-тестів падає з `ModuleNotFoundError`.
   - Юніт `test_monobank_service.py::test_connect_card_happy_path` очікує, що у
     середовищі задано `MONOBANK_WEBHOOK_URL` (як у `.env` / `.env.example`).
   Це питання налаштування оточення, а не дефект коду.

5. **WebSocket-стрічка (`/ws/feed`) повертає 404 у Docker-dev**
   У dev-режимі (`uvicorn ... --reload` без `uvicorn[standard]`) відсутня
   WebSocket-бібліотека, тому realtime-стрічка вимкнена і працює fallback через
   звичайні REST-запити. На основну функціональність застосунку не впливає
   (`VITE_REALTIME_MODE=off` за замовчуванням).

---

## 4. Висновок

Усі **89 тест-кейсів** (37 unit + 52 integration) проходять успішно — **100%**.
Критичних відкритих дефектів немає. Відомі зауваження мають характер технічного
боргу (deprecation warnings) або прерквізитів середовища і не впливають на
функціональність MVP. Продукт готовий до передачі (Handover).
