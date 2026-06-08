import { createRouter, createWebHistory } from 'vue-router'

const RegisterView = () => import('../views/RegisterView.vue')
const LoginView = () => import('../views/LoginView.vue')
const ForgotPasswordView = () => import('../views/ForgotPasswordView.vue')
const FeedView = () => import('../views/FeedView.vue')

// function hasValidToken() {
//   return !!localStorage.getItem('accessToken')
// }

function hasValidToken() {
  const token = localStorage.getItem('accessToken')
  if (!token) return false

  try {
    // JWT складається з трьох частин через крапку
    // payload — друга частина, закодована у base64
    const payload = JSON.parse(atob(token.split('.')[1]))
    // exp у JWT — це Unix timestamp у секундах
    const isExpired = payload.exp * 1000 < Date.now()
    if (isExpired) {
      localStorage.removeItem('accessToken')
      localStorage.removeItem('currentUser')
      return false
    }
    return true
  } catch {
    // Якщо токен зіпсований — чистимо і повертаємо false
    localStorage.removeItem('accessToken')
    localStorage.removeItem('currentUser')
    return false
  }
}

const routes = [
  {
    path: '/',
    redirect: () => {
      return hasValidToken() ? '/feed' : '/login'
    },
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { requiresGuest: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
    meta: { requiresGuest: true },
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: ForgotPasswordView,
    meta: { requiresGuest: true },
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: () => import('../views/ResetPasswordView.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/feed',
    name: 'Feed',
    component: FeedView,
    meta: { requiresAuth: true },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/SettingsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/group-setup',
    name: 'GroupSetup',
    component: () => import('../views/GroupSetupView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/gift-events',
    name: 'GiftEvents',
    component: () => import('../views/GiftEventsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/select-group',
    name: 'SelectGroup',
    component: () => import('../views/SelectGroupView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/gift-events/:id',
    name: 'GiftEventDetails',
    component: () => import('../views/GiftEventDetailsView.vue'),
    meta: { requiresAuth: true },
  },
  // Catch-all 404 — публічна, без redirect-guard'ів
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFoundView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach((to) => {
  const isAuthenticated = hasValidToken()

  if (to.meta.requiresAuth && !isAuthenticated) {
    return { name: 'Login' }
  }

  if (to.meta.requiresGuest && isAuthenticated) {
    return { name: 'Feed' }
  }
})

export default router
