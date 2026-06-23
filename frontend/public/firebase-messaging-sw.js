/* global importScripts, firebase, self */
// ============================================================
// Firebase Messaging Service Worker — фонові push-сповіщення
// (працює, навіть коли вкладку закрито).
//
// ⚠️ Service worker НЕ бачить змінні Vite (.env), тому конфіг тут
//    прописується вручну. Це ПУБЛІЧНІ значення web-конфігу — безпечно.
//    Заповни їх ТИМИ САМИМИ значеннями, що й у frontend/.env
//    (VITE_FIREBASE_*). Їх видає колега з backend (Firebase Console).
// ============================================================

importScripts('https://www.gstatic.com/firebasejs/10.12.0/firebase-app-compat.js')
importScripts('https://www.gstatic.com/firebasejs/10.12.0/firebase-messaging-compat.js')

firebase.initializeApp({
  apiKey: 'AIzaSyBuEQCPpEVLY2LG56Z3ko8yvFJ4Tw2AOOY',
  authDomain: 'familywallet-e34f8.firebaseapp.com',
  projectId: 'familywallet-e34f8',
  storageBucket: 'familywallet-e34f8.firebasestorage.app',
  messagingSenderId: '256158912328',
  appId: '1:256158912328:web:40d3bf8615687083c72d7d',
})

const messaging = firebase.messaging()

// Фонові повідомлення → системне сповіщення
messaging.onBackgroundMessage((payload) => {
  const title = (payload.notification && payload.notification.title) || 'Family Wallet'
  const options = {
    body: (payload.notification && payload.notification.body) || '',
    icon: '/favicon.ico',
  }
  self.registration.showNotification(title, options)
})
