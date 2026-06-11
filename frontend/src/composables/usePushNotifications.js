import { updateFcmToken } from '../services/notificationService'

let foregroundBound = false
let lastSyncedToken = null

export function usePushNotifications() {
  async function initPush() {
    if (!('serviceWorker' in navigator) || !('Notification' in window)) {
      return
    }

    try {
      const { getMessagingInstance, VAPID_KEY, isFirebaseConfigured } =
        await import('../services/firebase')
      if (!isFirebaseConfigured) {
        return
      }

      const messaging = await getMessagingInstance()
      if (!messaging) return

      const permission = await Notification.requestPermission()
      if (permission !== 'granted') {
        return
      }

      const registration = await navigator.serviceWorker.register('/firebase-messaging-sw.js')

      const { getToken, onMessage } = await import('firebase/messaging')
      const token = await getToken(messaging, {
        vapidKey: VAPID_KEY,
        serviceWorkerRegistration: registration,
      })
      if (!token) {
        return
      }

      if (token !== lastSyncedToken) {
        await updateFcmToken(token)
        lastSyncedToken = token
      }

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
    } catch {
      // Помилка ініціалізації push — push залишається вимкненим (тихий no-op)
    }
  }

  return { initPush }
}
