# Family Wallet

Веб-застосунок для управління сімейним бюджетом.

## Технології

- **Frontend:** Vue 3, Vue Router, Pinia, Axios, Vite
- **Backend:** FastAPI, Uvicorn, Motor (async MongoDB)
- **База даних:** MongoDB Atlas
- **Деплой:** Fly.io, GitHub Actions CI/CD
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

Необхідні змінні:

| Змінна       | Опис                              |
| ------------ | --------------------------------- |
| `MONGO_URI`  | Connection string для MongoDB Atlas |
| `SECRET_KEY` | Секретний ключ для JWT токенів    |

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

## Структура проєкту

```
Family-Wallet/
├── backend/
│   ├── app/              # FastAPI застосунок
│   │   └── main.py       # Точка входу API
│   ├── Dockerfile
│   ├── fly.toml          # Конфігурація Fly.io
│   └── requirements.txt
├── frontend/
│   ├── src/              # Vue 3 вихідний код
│   ├── Dockerfile        # Multi-stage build (Node + Nginx)
│   ├── nginx.conf        # Конфігурація Nginx для продакшену
│   ├── fly.toml          # Конфігурація Fly.io
│   └── package.json
├── .github/workflows/
│   └── deploy.yml        # CI/CD: автодеплой на Fly.io
├── docker-compose.yml    # Локальна розробка
└── .env.example          # Шаблон змінних середовища
```

## Деплой

Деплой відбувається автоматично через GitHub Actions при пуші в гілку `production`:

1. Backend деплоїться на Fly.io (`family-wallet-backend`)
2. Frontend деплоїться на Fly.io (`family-wallet-frontend`)

Для деплою потрібен секрет `FLY_API_TOKEN` в налаштуваннях репозиторію на GitHub.

## API

- `GET /health` — перевірка стану сервера
