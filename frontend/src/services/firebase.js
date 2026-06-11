import { initializeApp } from 'firebase/app'
import { getMessaging, isSupported } from 'firebase/messaging'

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
}

export const VAPID_KEY = import.meta.env.VITE_FIREBASE_VAPID_KEY

export const isFirebaseConfigured = Boolean(
  firebaseConfig.apiKey &&
  firebaseConfig.projectId &&
  firebaseConfig.appId &&
  firebaseConfig.messagingSenderId &&
  VAPID_KEY,
)

let messagingInstance = null

export async function getMessagingInstance() {
  if (!isFirebaseConfigured) return null
  if (!(await isSupported())) return null
  if (!messagingInstance) {
    const app = initializeApp(firebaseConfig)
    messagingInstance = getMessaging(app)
  }
  return messagingInstance
}
