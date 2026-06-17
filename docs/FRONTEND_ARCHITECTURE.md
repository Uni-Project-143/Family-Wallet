# Family Wallet — Frontend Architecture (пояснювальна записка)

Опис архітектури клієнтської частини: технологічний стек, структура, керування станом, взаємодія з API та real-time, стилі й надійність UX.

---

## 1. Технологічний стек

| Шар | Технологія | Призначення |
|---|---|---|
| Фреймворк | **Vue 3** (Composition API, `<script setup>`) | реактивний UI |
| Збірка / Build | **Vite 6** | dev-сервер, HMR, production-бандл |
| Маршрутизація | **Vue Router 4** | SPA-навігація, guard'и |
| HTTP | **Axios** | запити до REST API + interceptors |
| Real-time | **WebSocket** (native) + **Firebase Cloud Messaging** | живі оновлення + push |
| Ефекти | **canvas-confetti** | анімація розкриття Secret Gift |
| Мова | **JavaScript** (ESM) | без TypeScript |
| Стилі | **Custom CSS** (scoped per-SFC) | без CSS-фреймворків |

Жодних UI-бібліотек (Tailwind/Bootstrap/Vuetify) — інтерфейс повністю кастомний.

---

## 2. Структура проєкту

```
frontend/src/
├── views/         # сторінки-маршрути (FeedView, SettingsView, LoginView, GiftEvents…)
├── components/    # перевикористовувані блоки (модалки, картки, NavBar, ErrorBoundary)
├── composables/   # логіка та стан (useAuth, useFeedTransactions, useWebSocket…)
├── services/      # API-шар (apiClient + *Service.js)
├── utils/         # чисті функції (apiError, categoryColors, datetime…)
├── locales/       # i18n-рядки (en.js)
├── router/        # конфігурація маршрутів і guard'и
├── assets/        # глобальний main.css
├── App.vue        # кореневий компонент (RouterView + ErrorBoundary)
└── main.js        # точка входу (createApp)
```

**Принцип шарів:** `views` → `composables` (логіка/стан) → `services` (API) → backend. `utils` — чисті помічники без побічних ефектів. Така структура розділяє відповідальність: компонент відповідає лише за відображення, бізнес-логіка живе у composables, мережа — у services.

---

## 3. Керування станом (State Management)

Свідомо **без Pinia/Vuex**. Для MVP такого масштабу глобальний store надлишковий, тому стан керується **нативною реактивністю Vue + composables**:

- **Локальний стан** компонента — `ref` / `reactive` / `computed`.
- **Спільний (глобальний) стан** — composables зі станом на рівні модуля (singleton). Напр. `useAuth` тримає `currentUser` як модульний `ref`, тож усі компоненти бачать один і той самий стан користувача; `useReactions` так само тримає згруповані реакції.
- **Персистентний стан** — `usePersistentState(key, default)` синхронізує `ref` із `localStorage` (переживає reload): активний користувач, реакції, rate-limit.

> **Обґрунтування рішення:** composables дають перевикористання логіки без зайвого boilerplate глобального store; стан лежить поруч із логікою, що ним керує. Це масштабовано (легко винести в Pinia пізніше) і простіше для команди.

Ключові composables:

| Composable | Відповідальність |
|---|---|
| `useAuth` | сесія, логін/реєстрація/логаут, ролі, маршрутизація після входу |
| `useFeedTransactions` | стрічка транзакцій, пагінація (`loadMore`), `hasMore` |
| `useReactions` | emoji-реакції (оптимістичний апдейт + синк із сервером) |
| `useWebSocket` | WS-клієнт з auto-reconnect і ping/pong heartbeat |
| `usePushNotifications` | FCM push (лінива ініціалізація Firebase) |
| `useInfiniteScroll` | IntersectionObserver-обгортка (опційно) |
| `useFocusTrap` | доступність модалок (Tab-trap, inert) |
| `usePersistentState` | реактивне значення ↔ localStorage |

---

## 4. Взаємодія з API

Центральний **`apiClient`** (Axios) у `services/apiClient.js`:

- **Request interceptor** — додає `Authorization: Bearer <token>` з localStorage.
- **Response interceptor** — на кожну помилку прикріплює готове повідомлення `error.userMessage`; на `401` поза auth-ендпоінтами чистить сесію і редіректить на `/login`.
- **Централізація помилок** — `utils/apiError.js` мапить будь-яку помилку API у зрозумілий текст (мережа/таймаут/422/коди статусів), джерело текстів — `locales/en.js`.

Кожен домен має свій сервіс: `authService`, `cardService`, `giftEventService`, `moneyRequestService`, `notificationService`, `transactionService`. Компоненти **не** звертаються до axios напряму — лише через сервіси.

---

## 5. Маршрутизація та безпека доступу

`router/index.js` — `createWebHistory`, **lazy-loaded** компоненти (code-splitting).

- **Guard'и:** `requiresAuth` (перевірка валідності JWT — декодування `exp`, очистка простроченого) і `requiresGuest`.
- **Збереження цілі:** при редіректі неавторизованого на `/login` зберігається `?redirect=…`, і після входу користувач повертається на потрібний шлях (напр. secret-gift лінк).
- **404** — catch-all маршрут `/:pathMatch(.*)*` → `NotFoundView`.
- `scrollBehavior` повертає сторінку вгору при навігації.

---

## 6. Real-time (живі оновлення)

- **WebSocket** (`useWebSocket`): підключення до `ws://…/ws/feed/{group_id}`, **auto-reconnect** з exponential backoff і **heartbeat** (ping кожні 30с). Події `new_transaction`, `reaction_updated`, `new_request`/`request_updated` оновлюють стрічку, реакції та запити в реальному часі.
- **Push (FCM)** (`usePushNotifications`): Firebase SDK вантажиться **ліниво** (dynamic import) лише при ввімкненні push — щоб не роздувати початковий бандл (краще Lighthouse Performance). Нагадування Secret Gift приходять push-ом/email.

---

## 7. Стилі та адаптивність

- **Custom CSS**, переважно у `<style scoped>` кожного SFC; глобальна основа — `assets/main.css`; reset — у `index.html`.
- **Дизайн-токени** — як узгоджені конвенції (кольори/радіуси/тіні), описані у `docs/BRAND_STYLE_GUIDE.md`.
- **Адаптивність** — суто на **CSS media-queries** (брейкпоінти 768px / 480px): flex/grid-reflow, перепорядкування колонок (`order`), скрол-списки з `max-height`, адаптивна таблиця учасників. Без JS-залежності — працює автоматично при resize.

---

## 8. Надійність UX (UX Resilience)

- **Error Boundary** (`components/ErrorBoundary.vue`, `onErrorCaptured`) обгортає `RouterView` з `:key=route.fullPath` — помилка рендеру однієї сторінки показує fallback із Retry/Reload, а не кладе весь застосунок.
- **Порожні стани** — усюди замість безкінечного лоадера (`EmptyFeed`, заглушки списків).
- **Скелетони/лоадери** — `FeedSkeleton`, спінери на запитах.
- **Rate-limit логіну** — блок форми з точним відліком (синхронізовано з беком через `Retry-After`).

---

## 9. Якість і збірка

- **ESLint 10 + Prettier 3** (конвенції — у `STYLEGUIDE.md`); 0 помилок лінту.
- **Vite production build** — мініфікація, code-splitting по маршрутах.
- **Docker** — фронт піднімається через `docker-compose`.

---

## 10. Потік даних (Data Flow, спрощено)

```
Дія користувача → View (SFC)
        │
        ▼
   composable (стан + логіка)
        │
        ▼
   service → apiClient (Axios, interceptors) → Backend REST API
        ▲
        │  (паралельно)
   WebSocket / FCM → composable → реактивний стан → автооновлення View
```

Запит проходить через interceptor (токен, обробка помилок); відповідь оновлює реактивний стан у composable; Vue автоматично перемальовує View. Live-події (WS/push) оновлюють той самий стан, тож інтерфейс синхронний без ручного refetch.
