# Деплой Family-Wallet

Інфраструктура: **Backend** — Render.com (Docker), **Frontend** — Cloudflare Pages, **DB** — MongoDB Atlas.

- Backend (prod): https://family-wallet-backend-tb1v.onrender.com
- Frontend (prod): https://family-wallet.pages.dev

---

## 1. MongoDB Atlas

1. Створи cluster, користувача БД.
2. У `Network Access` → `Add IP Address` → **Allow access from anywhere** (`0.0.0.0/0`), бо Render використовує динамічні IP.
3. Скопіюй connection string у `MONGO_ATLAS`.

---

## 2. Backend — Render.com

### Сервіс
- Type: **Web Service**
- Environment: **Docker**
- Dockerfile path: `backend/Dockerfile`
- Docker context: `backend/`
- Branch: `production` (або та, з якої деплоїш)
- Health Check Path: `/health`
- Auto-deploy: On commit to branch

### Environment Variables (Render → Environment)
| Ключ | Значення |
| --- | --- |
| `MONGO_ATLAS` | mongodb+srv://... |
| `DB_NAME` | `FamilyWallet` |
| `JWT_SECRET` | згенеруй: `python -c "import secrets; print(secrets.token_urlsafe(64))"` |
| `MONOBANK_ENCRYPTION_KEY` | base64-32-байти: `python -c "import base64,os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"` |
| `MONOBANK_WEBHOOK_URL` | `https://family-wallet-backend-tb1v.onrender.com/api/v1/monobank/webhook` |
| `CORS_ORIGINS` | `https://family-wallet.pages.dev` |
| `CORS_ORIGIN_REGEX` (опц.) | `^https://.*\\.family-wallet\\.pages\\.dev$` — щоб дозволити preview-домени CFP |
| `ENV` | `production` |

> `PORT` Render проставляє автоматично — Dockerfile вже читає `$PORT`.

### Перевірка
```bash
curl https://family-wallet-backend-tb1v.onrender.com/health
# → {"status":"Database is healthy","code":200}
```

---

## 3. Frontend — Cloudflare Pages

### Налаштування білда
- Framework preset: **Vue** (або None)
- Build command: `npm install && npm run build`
- Build output directory: `dist`
- Root directory: `frontend`
- Production branch: `production`

### Environment Variables (Settings → Environment variables → Production)
| Ключ | Значення |
| --- | --- |
| `VITE_API_BASE_URL` | `https://family-wallet-backend-tb1v.onrender.com` |
| `VITE_WS_BASE_URL` | `wss://family-wallet-backend-tb1v.onrender.com/ws/feed` |
| `VITE_WS_ENABLED` | `true` |
| `VITE_REALTIME_MODE` | `ws` (або `off` якщо ще не готово) |

> Якщо `.env.production` лежить у репо (як зараз) — він підхопиться при білді й env-змінні в UI можна не дублювати. Але змінні в UI мають вищий пріоритет.

### SPA-fallback і кешування
- `frontend/public/_redirects` — fallback `/* → /index.html 200` для vue-router (history mode).
- `frontend/public/_headers` — кеш `assets/*` на рік + базові security-заголовки.

Vite копіює вміст `public/` у `dist/` під час білда, тож обидва файли потраплять на Cloudflare Pages.

---

## 4. Monobank webhook

Після деплою бекенду:
1. Перевір, що `MONOBANK_WEBHOOK_URL` вказує на прод-домен Render.
2. При підключенні картки бекенд сам зареєструє webhook через `POST https://api.monobank.ua/personal/webhook`. Перевір `GET /api/v1/monobank/webhook` → `{"message":"Webhook is ready"}`.

---

## 5. Чек-лист перед прод-релізом

- [ ] Усі env-змінні з `.env.example` задані на Render і Cloudflare Pages.
- [ ] `JWT_SECRET` НЕ дефолтний (`super-secret-key-for-development-only`).
- [ ] `MONGO_ATLAS` доступний з Render (Network Access відкритий).
- [ ] `CORS_ORIGINS` містить продакшен-домен фронту.
- [ ] `curl /health` повертає 200.
- [ ] Логін, реєстрація і feed працюють на https://family-wallet.pages.dev.
- [ ] WebSocket з’єднання встановлюється (Network → WS у DevTools).
