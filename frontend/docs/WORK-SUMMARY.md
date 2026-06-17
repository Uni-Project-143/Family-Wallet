# Звіт про виконану роботу (Frontend + інтеграція Secret Gift)

Документ для команди: **що додано/змінено і де**.
Backend змінювала **тільки** для усунення блокуючих багів (точково, позначено нижче).

---

## 0. Нові фічі стрічки (до Secret Gift)

| Що                                                                                     | Де                                                                                                     |
| -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Прокрутка списків у sidebar (≈5 видимих, далі скрол) — Group Members і Connected Cards | `views/FeedView.vue` (`.sidebar__scroll--members/--cards`)                                             |
| **Emoji-реакції на транзакціях** (Telegram-style: пікер 7 емодзі, toggle, персист)     | `components/TransactionCard.vue`, новий `composables/useReactions.js` (localStorage `fw_tx_reactions`) |

---

## 1. Secret Gift — інтеграція з реальним backend (EPIC 4)

Сервісний шар переведено із заглушок на **реальні endpoint'и** — `services/giftEventService.js`:

- `createGiftEvent` → `POST /api/v1/gift/create`
- `fetchGiftEventDetails` → `GET /api/v1/gift/{id}/details`
- `generateGiftInviteLink` → `POST /api/v1/gift/{id}/invite` (PROJ-57)
- `fetchGroupGiftEvents` → `GET /api/v1/gift/group/{group_id}` (PROJ-58, з ізоляцією)
- `contributeToGift` → `POST /api/v1/gift/{id}/contribute`

Де це використовується:

- `views/GiftEventsView.vue` — майстер створення події (форма, dropdown без self, авто-генерація invite).
- `views/GiftEventDetailsView.vue` — деталі, WOW-екран із конфеті, **секція внеску (Contribute)**.
- `views/FeedView.vue` — правий блок _Active Gift Events_ + pinned-банер на **реальних** подіях (мок «Sofia's Birthday» прибрано).

---

## 2. Як ПРАВИЛЬНО запускати Gift Event (таймзона + тест)

**Головне про дату розкриття (`unlock_date`):**

- У формі вводиш **локальний час** (свій настінний годинник). Фронт сам конвертує його в UTC:
  `unlock_date: new Date(form.unlockDate).toISOString()` (`views/GiftEventsView.vue`).
  Приклад: Київ `01:14` → зберігається `22:14Z`. **Нічого вручну не рахувати.**
- Через **Swagger** (без фронта) — UTC вписуєш вручну (Київ −3 год).
- Backend (cron) порівнює UTC з UTC і розкриває **точно о локальному часі**, який ти ввела.

**Алгоритм тесту розкриття:**

1. Організатор — один акаунт, **target = ти** (REVEAL іде лише імениннику).
2. Створити подію з `unlock_date` за ~2–3 хв (через UI).
3. До розкриття як target: у фіді секретних транзакцій немає, прямий лінк на подію → «Surprise in progress» (403).
4. Дочекатись cron (≤30 с після unlock) → у логах беку `РОЗКРИТО` → email/push + WOW-екран.

**Важливо для надійного тесту:** backend запускати **без `--reload`** (uvicorn `--reload` на збереженні файлу скасовує фоновий cron — і подія може не розкритись).

---

## 3. Push / Email сповіщення (EPIC 5, US.08)

**Email** — повністю backend (SendGrid), фронту не треба.
**Push (FCM)** — інтеграція з боку фронта (нове):

| Що                                                                           | Де                                         |
| ---------------------------------------------------------------------------- | ------------------------------------------ |
| Ініціалізація Firebase (web-config з env, ліниве завантаження SDK)           | `services/firebase.js`                     |
| Логіка push: дозвіл → токен → відправка на backend → foreground-повідомлення | `composables/usePushNotifications.js`      |
| Відправка токена `PUT /api/v1/auth/me/fcm-token`                             | `services/notificationService.js`          |
| Service worker для фонових пушів                                             | `public/firebase-messaging-sw.js`          |
| Виклик `initPush()` після login/register і при старті з валідним токеном     | `composables/useAuth.js`, `App.vue`        |
| Env-змінні Firebase                                                          | `.env`, `.env.example` (`VITE_FIREBASE_*`) |
| Пакет `firebase`                                                             | `package.json` (встановлено)               |

> Для роботи push потрібні: 7 значень `VITE_FIREBASE_*` у фронті (web-config + VAPID) і `firebase-adminsdk.json` + `FIREBASE_CREDENTIALS_PATH` на **backend**.

---

## 4. Виправлені баги (включно з backend — точково)

| Баг                                          | Причина                                                                 | Виправлення (де)                                                                                                                            |
| -------------------------------------------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Invite-лінк давав «CORS error»               | модель `GiftInvite` не зареєстрована в Beanie → 500 без CORS-заголовків | **backend** `config/database.py` (додано `GiftInvite` у `document_models`)                                                                  |
| Target бачив секретні транзакції             | ізоляція спиралась на `unlock_date > now` (крихко до tz/затримки cron)  | **backend** `api/feed.py` — ізоляція за статусом `ACTIVE` (поки подія не `REVEALED`)                                                        |
| Після розкриття target не мав входу до події | `GET /gift/group/{id}` повертав лише `ACTIVE`                           | **backend** `api/gift.py` — додано `REVEALED` (target отримує картку-вхід → WOW)                                                            |
| Розкриття «не в той час» / нема видимості    | потрібні діагностика + швидший тик                                      | **backend** `services/gift_service.py` — логи `[CRON]` + інтервал 30 с                                                                      |
| Email не приходив                            | відправку видно лише в логах                                            | **backend** `services/notification_service.py` — лог `[NOTIFY]` (одержувач)                                                                 |
| Дата події «з'їжджала» на день назад         | backend віддає наївний UTC без `Z` → JS читав як локальний час          | **frontend** новий `utils/datetime.js` `parseServerDate()`; застосовано в `GiftEventDetailsView.vue`, `FeedView.vue`, `TransactionCard.vue` |

---

## 5. Фіналізація UI / QA (Крок 2–5 завдання)

### 5.1 Error Handling (400/401/403/409/422/429/5xx)

- Новий `utils/apiError.js` — `getApiErrorMessage()`: бере конкретний `detail` з backend, обробляє валідацію 422, мережу/таймаут, дає осмислені фолбеки за статусом.
- `services/apiClient.js` — чіпляє `err.userMessage` до кожної помилки; на 401 поза auth → авто-logout + редірект на `/login`.
- Прибрано «Something went wrong» і неправильне читання `data.message` у: `useAuth.js`, `GiftEventsView.vue`, `GiftEventDetailsView.vue`, `ConnectCardModal.vue`, `GroupSetupView.vue`, `ForgotPasswordView.vue`, `FeedView.vue`, `SettingsView.vue`. (Також виправлено латентний баг у `GroupSetupView` — гілка «вже учасник» перевіряла не те поле.)

### 5.2 Zero Mocks (реальні дані замість заглушок)

- Donut **«Spending by Category»** — рахується з реальних транзакцій (`views/FeedView.vue`), а не хардкод.
- Панель **Notifications** — empty state (мок Sofia/Mykola прибрано).
- Прибрано: «Sofia's Birthday», «Neighborhood», кнопка «Переказ» з sidebar.

### 5.3 Локалізація / константи

- Новий `locales/en.js` — централізовані рядки (`common / empty / loading / errors`); `apiError.js` бере тексти звідси.

### 5.4 Empty / Loading states

- Додано: skeleton-завантаження + empty для Group Members, empty для Connected Cards, empty для donut/notifications (`views/FeedView.vue`). Решта (Feed, Donors, Event) уже мали стани.

### 5.5 Навігація / 404 / кнопки

- Нова сторінка `views/NotFoundView.vue` + catch-all маршрут `/:pathMatch(.*)*` у `router/index.js`.
- Аудит навігації: усі `router-link`/`router.push` ведуть на існуючі маршрути (битих немає).
- Double-click prevention: усі критичні async-кнопки `:disabled` під час запиту (перевірено, було вже на місці).

### 5.6 Динамічна валідація «на льоту»

- `views/RegisterView.vue` — вже мала (watchers + touched).
- `views/GiftEventsView.vue` — **додано** live-валідацію (`watch` на name/unlockDate/goalAmount/target).

### 5.7 Рефакторинг навбару

- Новий `components/NavBar.vue` (логотип + вкладки + user area + опц. logout + слот `#left`).
- Підключено у `FeedView`, `GiftEventsView`, `GiftEventDetailsView`, `SettingsView` (прибрано 4× дубльованої розмітки/CSS → бандли менші).

### 5.8 Responsive / Lighthouse / Perf

- **Responsive-баг:** `body { overflow: hidden }` обрізав контент на мобільному → `overflow-x: hidden` (`index.html`).
- **Performance:** Firebase SDK вантажиться **ліниво** (`usePushNotifications.js`) → головний бандл **−88 kB**.
- **SEO:** додано `meta description`, `theme-color`, описовий `<title>` (`index.html`).

---

## 6. Документація (артефакти для звіту)

| Файл                            | Що                                                                                               |
| ------------------------------- | ------------------------------------------------------------------------------------------------ |
| `frontend/docs/RTM-frontend.md` | Прив'язка User Stories (US.01–US.10) → frontend-файлів, статуси, обмеження                       |
| `frontend/docs/ARCHITECTURE.md` | Структура папок + опис глобального стану (composables + localStorage; Pinia не використовується) |
| `frontend/docs/WORK-SUMMARY.md` | Цей звіт                                                                                         |

---

## 7. Нові файли

```
frontend/src/composables/useReactions.js
frontend/src/composables/usePushNotifications.js
frontend/src/services/firebase.js
frontend/src/services/notificationService.js
frontend/src/components/NavBar.vue
frontend/src/views/NotFoundView.vue
frontend/src/utils/apiError.js
frontend/src/utils/datetime.js
frontend/src/locales/en.js
frontend/public/firebase-messaging-sw.js
frontend/docs/RTM-frontend.md
frontend/docs/ARCHITECTURE.md
frontend/docs/WORK-SUMMARY.md
```

## Backend — точкові правки (тільки фікси багів)

```
backend/app/config/database.py          # реєстрація моделі GiftInvite
backend/app/api/feed.py                 # ізоляція target за статусом ACTIVE
backend/app/api/gift.py                 # get_group_gifts: + REVEALED для target
backend/app/services/gift_service.py    # cron: логи + інтервал 30с
backend/app/services/notification_service.py  # лог [NOTIFY]
```

> Увага! Нагадування для безпеки: `firebase-adminsdk.json` має бути на **backend**, не у frontend; `.env` — у `.gitignore`; засвічені в чаті секрети (Mongo/SendGrid) бажано перевипустити.
