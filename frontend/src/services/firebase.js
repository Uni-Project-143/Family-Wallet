import { initializeApp } from 'firebase/app'
import { getMessaging, isSupported } from 'firebase/messaging'

/**
 * Firebase web-конфіг для Push (FCM).
 *
 * УВАГА: усі ці значення — ПУБЛІЧНІ (web config), їх безпечно тримати в клієнті.
 * Беруться зі змінних оточення Vite (.env). Значення видає колега з backend —
 * це той самий Firebase-проєкт, до якого належить його firebase-adminsdk.json.
 *
 * Якщо змінні не задані — push просто вимикається (додаток працює як завжди).
 */
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
}

// VAPID-ключ (Web Push certificate) з Firebase Console → Cloud Messaging.
export const VAPID_KEY = import.meta.env.VITE_FIREBASE_VAPID_KEY

// Чи задані мінімально потрібні значення, щоб push мав сенс.
export const isFirebaseConfigured = Boolean(
  firebaseConfig.apiKey &&
    firebaseConfig.projectId &&
    firebaseConfig.appId &&
    firebaseConfig.messagingSenderId &&
    VAPID_KEY,
)

let messagingInstance = null

/**
 * Лениво ініціалізує Firebase Messaging.
 * Повертає null, якщо конфіг відсутній або браузер не підтримує FCM.
 */
export async function getMessagingInstance() {
  if (!isFirebaseConfigured) return null
  if (!(await isSupported())) return null
  if (!messagingInstance) {
    const app = initializeApp(firebaseConfig)
    messagingInstance = getMessaging(app)
  }
  return messagingInstance
}
