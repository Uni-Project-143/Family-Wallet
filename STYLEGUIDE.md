# Code Style Guide — Family Wallet

> Обраний галузевий стандарт:
> - **Frontend (JavaScript / Vue):** [Airbnb Style Guide](https://github.com/airbnb/javascript) з адаптаціями під Vue 3.
> - **Backend (Python / FastAPI):** [PEP 8](https://peps.python.org/pep-0008/) — enforced через [Ruff](https://docs.astral.sh/ruff/).

---

## 1. Formatting

| Параметр | Frontend (JS / Vue) | Backend (Python) |
| --- | --- | --- |
| Відступ | **2 пробіли** | **4 пробіли** |
| Максимальна довжина рядка | **100** символів | **100** символів |
| Крапка з комою | **Ні** (без `;`) | N/A |
| Лапки | **Одинарні** `'...'` | **Подвійні** `"..."` |
| Trailing comma | **Так** (all) | **Так** (Ruff default) |
| Кінець рядка | `LF` | `LF` |

Конфігураційні файли:
- Frontend: `.prettierrc`, `eslint.config.js`
- Backend: `pyproject.toml` (секція `[tool.ruff]`)
- Загальне: `.editorconfig`

---

## 2. Naming Conventions

### 2.1 Frontend

| Елемент | Стиль | Приклад |
| --- | --- | --- |
| **Папки** | `kebab-case` | `user-profile/`, `transaction-list/` |
| **Компоненти (`.vue`)** | `PascalCase` | `TransactionCard.vue`, `UserAvatar.vue` |
| **Утиліти, хуки, сервіси (`.js`)** | `camelCase` | `useAuth.js`, `formatCurrency.js`, `apiClient.js` |
| **Стилі (CSS Modules)** | `PascalCase.module.css` | `TransactionCard.module.css` |
| **Змінні та функції** | `camelCase` | `getUserName`, `totalAmount` |
| **Константи** | `UPPER_SNAKE_CASE` | `MAX_RETRY_COUNT`, `API_BASE_URL` |
| **Props / Emits (Vue)** | `camelCase` | `userName`, `onSubmit` |
| **Events (HTML template)** | `kebab-case` | `@update-value`, `@close-modal` |

### 2.2 Backend

| Елемент | Стиль | Приклад |
| --- | --- | --- |
| **Папки (packages)** | `snake_case` | `user_service/`, `auth/` |
| **Файли модулів** | `snake_case` | `transaction_router.py`, `user_schemas.py` |
| **Класи** | `PascalCase` | `TransactionCreate`, `UserResponse` |
| **Функції та змінні** | `snake_case` | `get_user_by_id`, `total_amount` |
| **Константи** | `UPPER_SNAKE_CASE` | `ACCESS_TOKEN_EXPIRE`, `DB_NAME` |
| **Pydantic моделі** | `PascalCase` | `UserCreate`, `WalletUpdate` |
| **Router prefix** | `kebab-case` | `/api/user-wallets` |

### 2.3 База даних (MongoDB)

| Елемент | Стиль | Приклад |
| --- | --- | --- |
| **Колекції** | `snake_case`, **множина** | `users`, `transactions`, `wallet_members` |
| **Поля документів** | `snake_case`, **однина** | `first_name`, `created_at`, `wallet_id` |
| **Зовнішні посилання (FK)** | `сутність_id` | `user_id`, `wallet_id`, `category_id` |

> Колекції мають бути консистентні з Backend-моделями через ODM (Motor / Beanie).

---

## 3. Загальні правила іменування

### 3.1 Boolean змінні

Мають починатися з префіксів: `is`, `has`, `can`, `should`.

```javascript
// Frontend
const isLoading = ref(false)
const hasPermission = computed(() => ...)
const canEdit = true
```

```python
# Backend
is_active: bool = True
has_premium: bool = False
can_delete: bool = False
```

### 3.2 Абревіатури

Абревіатури пишуться як звичайні слова (не всі літери великі):

| Правильно | Неправильно |
| --- | --- |
| `getApiUrl` | `getAPIURL` |
| `HttpClient` | `HTTPClient` |
| `userId` | `userID` |
| `XmlParser` | `XMLParser` |
| `get_ui_config` | `get_UI_config` |

### 3.3 Заборонені "сміттєві" назви

Наступні назви **заборонені** для файлів, змінних та сутностей:

| Заборонено | Замінити на |
| --- | --- |
| `data` | `userData`, `transactionList`, `responsePayload` |
| `info` | `userDetails`, `walletInfo` → `walletSummary` |
| `temp` | `pendingTransaction`, `draftEntry` |
| `result` | `fetchedUsers`, `validationOutput` |
| `item` | `transaction`, `walletMember` |
| `obj` | конкретна назва сутності |
| `val` | конкретна назва значення |
| `stuff`, `thing` | конкретна назва |

> Виняток: `data` допускається лише в контексті API-відповідей (`response.data`) та деструктуризації бібліотечних об'єктів.

---

## 4. Comments & Documentation

### 4.1 Frontend (JSDoc)

Обов'язкові JSDoc-коментарі для:
- **Публічних composables (хуки)**
- **Утилітарних функцій**
- **Складних computed / watchers** (де логіка неочевидна)

```javascript
/**
 * Форматує суму у гривнях з копійками.
 * @param {number} amount - Сума в копійках
 * @returns {string} Відформатована сума, напр. "1 234,56 UAH"
 */
function formatCurrency(amount) {
  // ...
}
```

### 4.2 Backend (Docstrings)

Обов'язкові docstrings для:
- **Ендпоінтів (route handlers)** — FastAPI використовує їх для автогенерації документації
- **Сервісних функцій з бізнес-логікою**
- **Pydantic моделей** (field descriptions)

```python
async def create_transaction(wallet_id: str, payload: TransactionCreate) -> TransactionResponse:
    """Create a new transaction in the specified wallet.

    Args:
        wallet_id: The wallet to add the transaction to.
        payload: Transaction data from the client.

    Returns:
        The created transaction with generated ID and timestamp.
    """
```

### 4.3 Коли НЕ потрібні коментарі

- Код, який говорить сам за себе (`get_user_by_id`, `isLoading`)
- Закоментований код — **видаляти**, не залишати
- Коментарі типу `// increment counter` для `counter++`

---

## 5. Інструментарій

### 5.1 Linter + Formatter

| | Frontend | Backend |
| --- | --- | --- |
| **Linter** | ESLint 10 + eslint-plugin-vue | Ruff (lint) |
| **Formatter** | Prettier 3 | Ruff (format) |
| **Конфігурація** | `eslint.config.js`, `.prettierrc` | `pyproject.toml` |

### 5.2 Команди

```bash
# Frontend
npm run lint          # Перевірка ESLint
npm run lint:fix      # Автовиправлення ESLint
npm run format        # Форматування Prettier
npm run format:check  # Перевірка форматування

# Backend
ruff check app/       # Перевірка Ruff
ruff check app/ --fix # Автовиправлення Ruff
ruff format app/      # Форматування Ruff
ruff format --check app/  # Перевірка форматування

# Все разом (Makefile)
make lint             # Лінтери: frontend + backend
make format           # Форматування: frontend + backend
make check            # Повна перевірка якості
```

### 5.3 IDE Setup (VS Code)

Проєкт вже має налаштування у `.vscode/`:
- **`settings.json`** — Format on Save увімкнено, ESLint auto-fix on save
- **`extensions.json`** — рекомендовані розширення:
  - `esbenp.prettier-vscode` — Prettier
  - `dbaeumer.vscode-eslint` — ESLint
  - `Vue.volar` — Vue 3 support
  - `charliermarsh.ruff` — Ruff (Python)
  - `editorconfig.editorconfig` — EditorConfig

> При відкритті проєкту VS Code запропонує встановити рекомендовані розширення.
> Format on Save працює автоматично — код форматується при збереженні файлу.

---

## 6. Чеклист Code Review

При перегляді PR перевіряйте (див. також `.github/pull_request_template.md`):

- [ ] Naming conventions дотримані (цей документ)
- [ ] Лінтер не видає помилок
- [ ] Форматування перевірено
- [ ] Немає закоментованого коду
- [ ] Немає `console.log` / `debugger` / `print()`
- [ ] Boolean змінні мають префікс `is`/`has`/`can`/`should`
- [ ] Немає "сміттєвих" назв (`data`, `temp`, `info`)
- [ ] JSDoc/docstrings для публічних функцій
- [ ] Абревіатури написані як слова (`Api`, не `API`)
