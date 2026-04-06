# Data Flow & Interaction Specification-001

## Статус

**Accepted**

## Дата

06.04.2026


## Проєкт

Family Wallet — веб-застосунок для управління сімейним бюджетом


## 1. Високорівнева схема (High-Level Architecture)

Система базується на трирівневій моделі взаємодії з додатковим каналом реального часу:

```
┌───────────────────────┐         ┌───────────────────────┐         ┌───────────────────────┐
│    Frontend Layer      │  HTTP   │    Backend Layer       │  TCP    │     Data Layer         │
│       (Client)         │ ◄─────► │       (API)            │ ◄─────► │     (Storage)          │
│                        │  REST   │                        │         │                        │
│  Vue 3 + Pinia         │  JSON   │  FastAPI + Uvicorn     │  Motor  │  MongoDB Atlas         │
│  Vue Router            │         │  JWT Auth              │ (async) │                        │
│  Axios HTTP Client     │  WS/SSE │  Pydantic Validation   │         │  Колекції:             │
│                        │ ◄─────► │  WebSocket / SSE       │         │  - users               │
│  Порт: 5173 (dev)      │         │                        │         │  - bankCards           │
│  Nginx (prod)          │         │  Порт: 8000            │         │  - transactions        │
│                        │         │                        │         │  - gift_events         │
└───────────────────────┘         └───────────────────────┘         │  - money_requests      │
                                            ▲                        └───────────────────────┘
                                            │  POST webhook
                                   ┌────────┴──────────┐
                                   │   Monobank API     │
                                   │  (External Source) │
                                   └───────────────────┘
```

**Frontend Layer (Client):**
Побудований на Vue 3 з Pinia для управління станом. Відповідає за UI, клієнтську валідацію форм, маршрутизацію (Vue Router). JWT-токен зберігається **виключно в httpOnly Secure Cookie** (не в localStorage/sessionStorage — NFR-02). Спілкується з Backend через REST API (Axios) та WebSocket/SSE для real-time оновлень.

**Backend Layer (API):**
Побудований на FastAPI. Виконує роль REST API сервера: приймає запити, валідує дані через Pydantic-схеми, виконує бізнес-логіку та повертає JSON-відповіді. Відповідає за автентифікацію (JWT у httpOnly Cookie), авторизацію (перевірка членства в гаманці), ізоляцію Target User в Secret Gift Mode та обробку вебхуків від Monobank.

**Data Layer (Storage):**
MongoDB Atlas (хмарна NoSQL база даних). Забезпечує збереження колекцій `users`, `bankCards`, `transactions`, `gift_events`, `money_requests`. Доступ здійснюється через Motor — асинхронний Python-драйвер для MongoDB.

---

## 2. Сценарії взаємодії (Data Flow)

### Сценарій А: Підключення Monobank та обробка Webhook (Epic 2)

Це основний технічний потік продукту. Транзакції **не вводяться вручну** — вони надходять автоматично через Monobank Open API.

#### А.1 — Підключення картки (US 2.1)

```
Admin ──► Frontend ──► Backend ──► MonobankService ──► Monobank API
  │                                                          │
  ◄──────────────── Response (200 OK + Card connected) ◄─────┘
```

1. **Admin:** Вводить Personal Token Monobank на сторінці підключення. Встановлює opt-in чекбокс згоди на обробку даних (GDPR / NFR-06).
2. **Frontend:** Відправляє `POST /api/v1/monobank/connect` з `MonobankConnectDTO` (token) та Bearer Cookie.
3. **Backend:** Перевіряє JWT, верифікує роль Admin (не-Admin → `403 Forbidden`). `MonobankService` звертається до Monobank API (`GET https://api.monobank.ua/personal/client-info`) для валідації токена та отримання списку рахунків. Реєструє Webhook URL (`POST /personal/webhook`) у Monobank API.
4. **MongoDB:** Зберігає зашифрований токен та metadata картки у колекції `bankCards`.
5. **Backend:** Повертає `200 OK` з `CardConnectedDTO` (card_id, masked_number, balance).

#### А.2 — Отримання та обробка Webhook (US 2.2)

```
Monobank API ──► Backend (POST /webhook/monobank) ──► WebhookService ──► MongoDB
                                                             │
                      Frontend (SSE/WS) ◄──── BroadcastService ◄───────────┘
                            │
                      All Group Members ──► Family Feed updated (≤ 5 сек)
```

1. **Monobank API:** При кожній транзакції надсилає `POST /api/v1/webhook/monobank` з підписаним payload (account, statementItem: id, time, description, amount, mcc, balance).
2. **Backend (WebhookController):** Верифікує підпис запиту. Перевіряє idempotency за `statementItem.id` — якщо транзакція вже існує в `transactions`, повертає `200 OK` без повторного збереження (захист від дублікатів).
3. **WebhookService:** Визначає `bankCards_id` та `user_id` за `account`. Збагачує транзакцію: категорія (MCC-код → category_name), `created_at`. Перевіряє, чи не є транзакція пов'язаною з активним Secret Gift Event (якщо так — позначає `is_gift_related: true` для подальшої ізоляції).
4. **MongoDB:** Зберігає документ у колекцію `transactions`.
5. **BroadcastService:** Надсилає SSE-подію або WebSocket-повідомлення всім підключеним учасникам групи **крім Target User**, якщо транзакція позначена `is_gift_related`.
6. **Frontend:** Pinia store оновлює Family Feed без перезавантаження сторінки. Загальний час від транзакції до відображення у feed: **p95 ≤ 5 секунд** (NFR-01).

---

### Сценарій Б: Сімейна Стрічка Транзакцій з Real-time оновленням (Epic 3)

```
User ──► Frontend ──► GET /api/v1/bankCards/{id}/feed ──► FeedService ──► MongoDB
  │                                                                          │
  ◄──────────── Response (200 OK + transactions[] + user avatars) ◄──────────┘
  │
  └── SSE: GET /api/v1/events/feed  (long-lived connection)
       └── Server pushes new_transaction events in real-time
```

1. **User:** Відкриває головний екран (Family Feed).
2. **Frontend:** Виконує два паралельних запити:
   - `GET /api/v1/bankCards/{bankCards_id}/feed?limit=20&offset=0` — початкове завантаження стрічки.
   - Відкриває SSE-з'єднання `GET /api/v1/events/feed` для real-time оновлень.
3. **Backend:** `FeedService` перевіряє членство користувача в групі. Якщо поточний користувач є **Target User** активного Gift Event — виключає з вибірки транзакції з `is_gift_related: true` (ізоляція, Rule-01).
4. **MongoDB:** Повертає транзакції з агрегацією даних про авторів (ім'я, avatar_url) через `$lookup` з колекції `users`.
5. **Backend:** Повертає `200 OK` з `FeedResponseDTO` (transactions[], total_count, has_more).
6. **Frontend:** Pinia store кешує транзакції. Компонент відображає стрічку з аватарами та іменами власників (US 3.2). При надходженні SSE-події `new_transaction` — prepend до списку без перезавантаження.

---

### Сценарій В: Secret Gift Mode (Epic 4 — Killer Feature)

#### В.1 — Створення Gift Event та генерація invite-лінку (US 4.1–4.3)

```
Organizer ──► Frontend ──► POST /api/v1/gift/create ──► GiftService ──► MongoDB
     │                                                                        │
     ◄──── Response (201 Created + gift_id + invite_link) ◄───────────────────┘
                                    │
                        ◄ 30 секунд від початку UX-сценарію (NFR-04)
```

1. **Organizer:** На екрані «Створити подарунок» обирає Target User зі списку учасників групи, вводить назву події та встановлює UnlockDate (дата не може бути в минулому — валідація на клієнті та сервері).
2. **Frontend:** Відправляє `POST /api/v1/gift/create` з `CreateGiftDTO` (target_user_id, title, unlock_date, group_id).
3. **Backend:** Перевіряє JWT та роль. `GiftService` валідує: target_user_id є членом групи; unlock_date > now(). Генерує унікальний `invite_token` (UUID v4). Зберігає документ у колекцію `gift_events` зі статусом `active`.
4. **MongoDB:** Зберігає `gift_event` (id, group_id, organizer_id, target_user_id, title, unlock_date, invite_token, status: "active", participants: []).
5. **Backend:** Повертає `201 Created` з `GiftCreatedDTO` (gift_id, invite_link: `https://app/join-gift/{invite_token}`).
6. **Frontend:** Відображає готове посилання з кнопкою «Поділитись». Весь UX-сценарій від першого кроку до отримання лінку — **≤ 30 секунд** (NFR-04).

#### В.2 — Ізоляція Target User (US 4.4)

```
Target User ──► GET /api/v1/gift/{id}/details
                         │
                    GiftService: перевірка (current_user_id === target_user_id) AND (now() < unlock_date)
                         │
                    ◄── 403 Forbidden (у 100% випадків до UnlockDate — NFR-02)
```

- **Механізм ізоляції діє на двох рівнях:**
  1. **API-рівень:** `GiftService.check_access()` у кожному запиті до `/api/v1/gift/{id}/*` порівнює `current_user_id` з `target_user_id` документа та перевіряє `unlock_date`. Target User отримує `403 Forbidden` у 100% випадків.
  2. **Feed-рівень:** Транзакції з `is_gift_related: true` фільтруються з Family Feed для Target User (Сценарій В, крок 3).

#### В.3 — Розкриття події після UnlockDate (US 4.5)

```
[Scheduler: cron job / APScheduler]
    └── Кожну хвилину: find gift_events WHERE unlock_date <= now() AND status == "active"
              └── GiftService.unlock(gift_id)
                       ├── Оновити status → "unlocked" у MongoDB
                       └── NotificationService: push/email до Target User + всіх учасників
                                  └── Frontend (SSE): event gift_unlocked → Target User тепер бачить деталі
```

- Після `unlock_date` Target User при зверненні до `GET /api/v1/gift/{id}/details` отримує `200 OK` з повними деталями збору.
- Push/email нагадування надсилаються за 1 день до та в момент розкриття (US 5.1).

---

### Сценарій Г: Money Request — Запит на Переказ (Epic 6)

#### Г.1 — Надсилання запиту (US 6.1)

```
Requester ──► POST /api/v1/requests ──► MoneyRequestService ──► MongoDB
                                                  │
                              WebSocket/SSE event ──► Recipient (модалка ≤ 2 сек)
```

1. **Requester:** Обирає учасника групи, вводить суму та опис.
2. **Frontend:** Відправляє `POST /api/v1/requests` з `CreateRequestDTO` (recipient_id, amount, description).
3. **Backend:** Валідує, що `requester_id !== recipient_id` (у 100% випадків → `400 Bad Request`). Зберігає документ у `money_requests` зі статусом `pending`. `BroadcastService` надсилає WebSocket-подію `new_money_request` до Recipient.
4. **MongoDB:** Зберігає `money_request` (id, requester_id, recipient_id, amount, description, status: "pending", created_at).

#### Г.2 — Відповідь на запит (US 6.2)

```
Recipient ──► WebSocket event new_money_request ──► Модальне вікно (≤ 2 сек)
     │
     └── PATCH /api/v1/requests/{id} ──► MoneyRequestService ──► MongoDB
              └── status: "accepted" | "rejected"
                       │
              WebSocket event request_resolved ──► Requester (оновлення статусу)
```

1. **Frontend (Recipient):** При отриманні WS-події `new_money_request` автоматично відображає модальне вікно із запитом (latency ≤ 2 сек від події, e2e тест).
2. **Recipient:** Натискає «Прийняти» або «Відхилити».
3. **Frontend:** Відправляє `PATCH /api/v1/requests/{id}` з `UpdateRequestDTO` (status: "accepted" | "rejected").
4. **Backend:** Оновлює статус у MongoDB. Надсилає WS-подію `request_resolved` до Requester.
5. **Frontend (Requester):** Оновлює статус запиту в інтерфейсі.

---

## 3. Механізм передачі даних та Statelessness

### JWT та Cookie-стратегія (NFR-02)

На відміну від v1, JWT **не зберігається в localStorage**. Використовується httpOnly Cookie:

| Параметр | Значення | Причина |
|---------|---------|---------|
| Storage | `httpOnly Secure Cookie` | Недоступний через JS → захист від XSS |
| SameSite | `Strict` | Захист від CSRF |
| Access Token TTL | 15 хвилин | NFR-02 |
| Refresh Token TTL | 7 днів | NFR-02 |
| Оновлення | `POST /api/v1/auth/refresh` | Автоматично через Axios interceptor при 401 |

### Використання DTO (Data Transfer Objects)

Ми **не передаємо сутності бази даних (Models) безпосередньо на фронтенд.** Pydantic-схеми виконують три функції:

1. **Валідація вхідних даних:** `CreateGiftSchema` перевіряє, що `unlock_date` > now(), `target_user_id` є членом групи.
2. **Фільтрація вихідних даних:** `GiftDetailsSchema` для Target User до UnlockDate → `403` (не повертає схему взагалі).
3. **Декаплінг:** Зміна структури документа в MongoDB не впливає на API-контракт.

**Зведена таблиця DTO:**

| Сценарій | Request DTO | Response DTO |
|---------|-------------|--------------|
| Логін | `LoginSchema` (email, password) | Set-Cookie (httpOnly JWT) |
| Webhook від Monobank | Internal: `MonobankWebhookPayload` | `200 OK` (no body) |
| Family Feed | Query params (limit, offset) | `FeedResponseSchema` (transactions[], has_more) |
| Створення Gift Event | `CreateGiftSchema` (target_user_id, title, unlock_date) | `GiftCreatedSchema` (gift_id, invite_link) |
| Деталі Gift (після UnlockDate) | — | `GiftDetailsSchema` (participants[], amounts[], total) |
| Money Request | `CreateRequestSchema` (recipient_id, amount, description) | `MoneyRequestSchema` (id, status) |

### Принцип Statelessness

Backend **не зберігає стан користувача** (Session ID) у пам'яті:

- Кожен HTTP-запит від Frontend містить JWT у httpOnly Cookie.
- Токен містить `{user_id, email, role}` — сервер не потребує додаткових lookups для ідентифікації.
- **Виняток:** WebSocket/SSE з'єднання зберігають стан підключення in-memory або через Redis Pub/Sub для broadcasting. Це не порушує Stateless-принцип для бізнес-логіки.
- **Стан застосунку зберігається у двох місцях:**
  - **JWT Cookie** (на клієнті) — ідентифікація та авторизація.
  - **MongoDB** (на сервері) — всі бізнес-дані (transactions, gift_events, money_requests, users, bankCards).

