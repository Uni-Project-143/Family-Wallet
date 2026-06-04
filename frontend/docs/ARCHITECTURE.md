# Frontend Architecture

**Стек:** Vue 3 (`<script setup>`) · Vue Router 4 · Vite 6 · Axios.
**Глобальний стан:** composables + module-level refs + `localStorage` (Pinia встановлено, але **не використовується**).

## Структура папок (`frontend/src`)

```
src/
├─ main.js                # точка входу: createApp(App).use(router).mount('#app')
├─ App.vue                # <RouterView/> + ініціалізація push при старті
│
├─ router/
│  └─ index.js            # маршрути, JWT-guard'и (requiresAuth/requiresGuest), catch-all 404
│
├─ views/                 # сторінки (1:1 з маршрутами)
│  ├─ LoginView.vue        RegisterView.vue       ForgotPasswordView.vue
│  ├─ GroupSetupView.vue   SelectGroupView.vue
│  ├─ FeedView.vue        # головна стрічка + sidebar + right panel
│  ├─ GiftEventsView.vue  # майстер створення Secret Gift
│  ├─ GiftEventDetailsView.vue  # деталі / WOW-екран / contribute
│  ├─ SettingsView.vue
│  └─ NotFoundView.vue    # 404
│
├─ components/            # переюзабельний UI
│  ├─ NavBar.vue          # спільний навбар (вкладки + user area + logout slot)
│  ├─ TransactionCard.vue # картка транзакції + emoji-реакції
│  ├─ ConnectCardModal.vue  CardDetailsModal.vue  ConnectCardReminderModal.vue
│  ├─ InviteMemberModal.vue TransferModal.vue     ConfirmDialog.vue
│  ├─ FeedSkeleton.vue    EmptyFeed.vue           ConnectionIndicator.vue
│  ├─ UserAvatar.vue      BaseInput.vue
│
├─ composables/          # логіка стану та побічні ефекти (Vue Composition API)
│  ├─ useAuth.js          # ⭐ глобальний auth-стан (singleton)
│  ├─ usePersistentState.js  # ref ↔ localStorage
│  ├─ useReactions.js     # ⭐ глобальний стан реакцій (singleton, localStorage)
│  ├─ usePushNotifications.js # FCM: дозвіл, токен, onMessage
│  ├─ useFeedTransactions.js  # пагінація стрічки
│  ├─ useInfiniteScroll.js    useWebSocket.js     useFocusTrap.js
│
├─ services/             # HTTP-шар (тонкі обгортки над apiClient)
│  ├─ apiClient.js        # ⭐ axios instance: Bearer-інтерсептор, 401-redirect, err.userMessage
│  ├─ authService.js      cardService.js          transactionService.js
│  ├─ giftEventService.js notificationService.js  firebase.js
│
├─ utils/                # чисті хелпери
│  ├─ apiError.js         # мапа помилок API → текст (джерело — locales/en.js)
│  ├─ datetime.js         # parseServerDate (наївний UTC → коректний Date)
│  ├─ authRateLimit.js    cardReminder.js
│
└─ locales/
   └─ en.js               # централізовані рядки: common / empty / loading / errors

public/
└─ firebase-messaging-sw.js  # service worker для фонових push
```

## Глобальний стан (без Pinia)

Стан тримається у **module-level `ref`** усередині composables — імпорт composable дає той самий singleton у будь-якому компоненті.

| Домен | Де | Як зберігається | Хто читає |
|---|---|---|---|
| **Auth / поточний користувач** | `useAuth.js` — `currentUser` (module-level ref) | `localStorage: accessToken, currentUser` | NavBar, усі views, apiClient (через токен) |
| **Активна група** | `useAuth.setActiveGroup` → `currentUser.groupId/role` | `localStorage` | Feed, Settings, Gift* |
| **Emoji-реакції** | `useReactions.js` — `myReactions` (singleton) | `localStorage: fw_tx_reactions` | TransactionCard |
| **FCM-токен (sync-стан)** | `usePushNotifications.js` (module-level прапорці) | надсилається на backend | App.vue, useAuth |
| **Будь-який persist-стан** | `usePersistentState(key, default)` | `localStorage[key]` | за потреби |

**Чому без Pinia:** стан простий і доменно-локалізований; singleton-composables дають реактивність + персист без зайвого boilerplate. Якщо стан ускладниться (offline-черги, оптимістичні апдейти) — `store/` готова під Pinia.

## Потік даних (типовий запит)

```
View / Composable
   → services/*.js  (apiClient.<method>)
      → apiClient інтерсептори: + Bearer, ← err.userMessage / 401-redirect
         → backend (FastAPI, /api/v1/*)
   ← дані → ref у composable/view → реактивний рендер
```

## Маршрутизація та доступ

- `createWebHistory` (History API; кнопка «Назад» працює нативно).
- Guard `beforeEach`: `requiresAuth` → `/login` без валідного JWT; `requiresGuest` → `/feed` якщо вже залогінений.
- `/` редіректить на `/feed` або `/login` за наявністю токена.
- Catch-all `/:pathMatch(.*)*` → `NotFoundView` (публічний).

## Обробка помилок

`apiClient` на кожну помилку чіпляє `err.userMessage` (через `utils/apiError.js`, тексти з `locales/en.js`): конкретний `detail` з backend або осмислений фолбек за статусом (400/401/403/409/422/429/5xx) + мережа/таймаут. 401 поза auth-ендпоінтами → авто-logout + редірект.
