import { updateFcmToken } from '../services/notificationService'

/**
 * Push-сповіщення через Firebase Cloud Messaging (FCM).
 *
 * Firebase SDK вантажиться ЛІНИВО (dynamic import) лише коли реально вмикаємо push,
 * щоб не роздувати початковий бандл (краще Lighthouse Performance).
 *
 * Сценарій initPush() (викликати після автентифікації / при старті з валідним токеном):
 *  1. Перевіряємо підтримку браузера та конфіг.
 *  2. Запитуємо дозвіл на сповіщення.
 *  3. Реєструємо service worker (firebase-messaging-sw.js) — для фонових пушів.
 *  4. Отримуємо FCM-токен пристрою.
 *  5. Відправляємо токен на backend (PUT /auth/me/fcm-token).
 *  6. Підписуємось на foreground-повідомлення.
 *
 * Якщо Firebase не налаштований / дозвіл не надано — тихий no-op.
 */

let foregroundBound = false
let lastSyncedToken = null

export function usePushNotifications() {
  async function initPush() {
    if (!('serviceWorker' in navigator) || !('Notification' in window)) {
      console.info('[Push] Браузер не підтримує service workers / Notifications.')
      return
    }

    try {
      // Ліниво підвантажуємо обгортку Firebase
      const { getMessagingInstance, VAPID_KEY, isFirebaseConfigured } = await import(
        '../services/firebase'
      )
      if (!isFirebaseConfigured) {
        console.info('[Push] Firebase не налаштовано (VITE_FIREBASE_* відсутні) — push вимкнено.')
        return
      }

      const messaging = await getMessagingInstance()
      if (!messaging) return

      // 2. Дозвіл на сповіщення
      const permission = await Notification.requestPermission()
      if (permission !== 'granted') {
        console.info('[Push] Дозвіл на сповіщення не надано.')
        return
      }

      // 3. Реєструємо service worker для фонових пушів
      const registration = await navigator.serviceWorker.register('/firebase-messaging-sw.js')

      // 4. Отримуємо FCM-токен пристрою (firebase/messaging — теж ліниво)
      const { getToken, onMessage } = await import('firebase/messaging')
      const token = await getToken(messaging, {
        vapidKey: VAPID_KEY,
        serviceWorkerRegistration: registration,
      })
      if (!token) {
        console.warn('[Push] Не вдалося отримати FCM-токен.')
        return
      }

      // 5. Відправляємо токен на backend (один раз на токен)
      if (token !== lastSyncedToken) {
        await updateFcmToken(token)
        lastSyncedToken = token
        console.info('[Push] FCM-токен синхронізовано з backend.')
      }

      // 6. Foreground-повідомлення (коли вкладка відкрита й активна)
      if (!foregroundBound) {
        onMessage(messaging, (payload) => {
          const title = payload.notification?.title || 'Family Wallet'
          const body = payload.notification?.body || ''
          try {
            new Notification(title, { body, icon: '/favicon.ico' })
          } catch {
            // Деякі браузери блокують Notification у foreground — ігноруємо
          }
        })
        foregroundBound = true
      }
    } catch (err) {
      console.warn('[Push] Помилка ініціалізації push:', err)
    }
  }

  return { initPush }
}
