# Family Wallet

Веб-застосунок для управління сімейним бюджетом.

## Технології

- **Frontend:** Vue 3, Vue Router, Pinia, Axios, Vite
- **Backend:** FastAPI, Uvicorn, Motor (async MongoDB)
- **База даних:** MongoDB Atlas
- **Деплой:** Cloudflare Pages (frontend), Render.com (backend), GitHub Actions CI/CD
- **Контейнеризація:** Docker, Docker Compose

## Вимоги

- [Docker](https://docs.docker.com/get-docker/) та [Docker Compose](https://docs.docker.com/compose/install/)
- Або для локального запуску без Docker:
  - Python 3.12+
  - Node.js 20+
  - npm

## Налаштування змінних середовища

Скопіюйте `.env.example` в `.env` та заповніть значення:

```bash
cp .env.example .env
```

Повний перелік змінних — у файлі [`.env.example`](.env.example) (джерело правди). Основні:

**Backend:**

| Змінна                    | Опис                                                        |
| ------------------------- | ----------------------------------------------------------- |
| `MONGO_ATLAS`             | Connection string для MongoDB Atlas                         |
| `DB_NAME`                 | Назва бази даних (за замовчуванням `FamilyWallet`)          |
| `JWT_SECRET`              | Секретний ключ для JWT токенів                              |
| `MONOBANK_ENCRYPTION_KEY` | AES-256 ключ (base64) для шифрування токенів Monobank       |
| `MONOBANK_WEBHOOK_URL`    | Публічний https URL бекенду для webhook'ів Monobank         |
| `CORS_ORIGINS`            | Дозволені origins фронтенду через кому                      |
| `ENV`                     | `development` / `production` (активує fail-fast для секретів) |

**Frontend (Vite):**

| Змінна               | Опис                                          |
| -------------------- | --------------------------------------------- |
| `VITE_API_BASE_URL`  | URL бекенд-API (напр. `http://localhost:8000`) |
| `VITE_WS_BASE_URL`   | URL WebSocket-стрічки                          |
| `VITE_WS_ENABLED`    | Увімкнення WebSocket (`true`/`false`)          |
| `VITE_REALTIME_MODE` | Режим реального часу: `off` / `ws` / `polling` |

## Запуск через Docker Compose (рекомендовано)

```bash
docker-compose up --build
```

Це запустить:
- **Backend** на `http://localhost:8000` (з hot reload)
- **Frontend** на `http://localhost:5173` (з hot reload)

Для запуску у фоновому режимі:

```bash
docker-compose up --build -d
```

Зупинити контейнери:

```bash
docker-compose down
```

## Тестові доступи (Credentials)

Для входу в систему під час перевірки використовуйте тестовий обліковий запис:

| Поле   | Значення           |
| ------ | ------------------ |
| Email  | `admin@gmail.com`  |
| Пароль | `Administrator`    |

Роль: **Administrator**. Обліковий запис вже створений у тестовій базі (MongoDB Atlas), додаткова реєстрація не потрібна.

## Локальний запуск без Docker

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API буде доступне на `http://localhost:8000`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Застосунок буде доступний на `http://localhost:5173`

## Деплой

Деплой відбувається автоматично при пуші в гілку `production`:

1. Backend деплоїться на Render.com — https://family-wallet-backend-tb1v.onrender.com/
2. Frontend деплоїться на Cloudflare Pages — https://family-wallet.pages.dev/

## Code Style

Проєкт дотримується задокументованих стандартів коду. Детальний опис правил — у файлі [`STYLEGUIDE.md`](STYLEGUIDE.md).

Короткий огляд:
- **Frontend:** [Airbnb Style Guide](https://github.com/airbnb/javascript), ESLint + Prettier, 2 пробіли, без `;`
- **Backend:** [PEP 8](https://peps.python.org/pep-0008/), Ruff, 4 пробіли, подвійні лапки
- **Format on Save** налаштовано у `.vscode/settings.json`

```bash
make check    # Перевірка лінтерів + форматування
make lint-fix # Автовиправлення лінтерів
make format   # Автоформатування
```

## Тестування

```bash
cd backend
pip install -r requirements.txt   # одноразово (включно з firebase-admin/sendgrid)
pytest                            # усі тести
pytest tests/unit                 # лише unit
pytest tests/integration          # лише integration
```

Підсумок фінального тестування (статистика, середовище, known issues) — у файлі
[`docs/TEST_SUMMARY_REPORT.md`](docs/TEST_SUMMARY_REPORT.md). Поточний статус: **89 тестів, 100% passed**.

## Архітектурна документація

- [Architectural Decision Record: System Style](docs/Architectural%20Decision%20Record%20-%20System%20Style.md) — обґрунтування вибору архітектурного стилю (Modular Monolith)
- [Software Architecture Document: Internal View](docs/Software%20Architecture%20Document%20-%20Internal%20View.md) — вибір внутрішнього архітектурного патерну (Layered Architecture)
- [Data Flow & Interaction Specification](docs/Data%20Flow%20%26%20Interaction%20Specification.md) — потоки даних та взаємодія компонентів

## Структура проєкту

```
Family-Wallet/
├── docs/                          # Документація, ТЗ, діаграми, API-специфікації
├── backend/                       # Backend-частина (Сервер)
│   └── app/
│       ├── api/                   # Presentation Layer — роутери, HTTP-ендпоінти
│       ├── services/              # Business Logic Layer — сценарії використання
│       ├── repositories/          # Data Access Layer — робота з MongoDB
│       ├── models/                # Структури даних (Entities)
│       ├── schemas/               # DTO — контракти API (Pydantic)
│       ├── middleware/            # JWT авторизація, CORS, обробка помилок
│       ├── config/                # Налаштування підключень, змінні середовища
│       └── main.py                # Точка входу FastAPI
├── frontend/                      # Frontend-частина (Клієнт)
│   └── src/
│       ├── components/            # UI-компоненти (кнопки, картки, форми)
│       ├── views/                 # Сторінки (Login, Dashboard, Wallet)
│       ├── services/              # API-клієнт (Axios запити до Backend)
│       ├── store/                 # Pinia — глобальний стан
│       ├── hooks/                 # Composables — винесена логіка поведінки
│       └── assets/                # Статичні ресурси (зображення, шрифти, стилі)
├── shared/                        # Спільні ресурси (типи, константи)
├── deploy/                        # Конфігурації для Docker, CI/CD, скрипти розгортання
├── .github/workflows/             # CI/CD: автодеплой (Cloudflare Pages + Render.com)
├── docker-compose.yml             # Локальна розробка
├── .editorconfig                  # Загальні правила форматування
└── .env.example                   # Шаблон змінних середовища
```
