import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { loginUser, registerUser, fetchMyGroups, logoutUser } from '../services/authService'
import { scheduleAfterRegistration } from '../utils/cardReminder'
import { usePushNotifications } from './usePushNotifications'

const STORAGE_TOKEN_KEY = 'accessToken'
const STORAGE_USER_KEY = 'currentUser'

function parseStoredUser() {
  try {
    const raw = localStorage.getItem(STORAGE_USER_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

const currentUser = ref(parseStoredUser())
const isLoading = ref(false)
const authError = ref(null)

function persistAuthSession(token, user) {
  localStorage.setItem(STORAGE_TOKEN_KEY, token)
  localStorage.setItem(STORAGE_USER_KEY, JSON.stringify(user))
  currentUser.value = user
}

/**
 * Зберігає активну групу окремо. При перемиканні груп — оновлюємо лише цей кусочок,
 * не чіпаючи fullName/email юзера.
 */
function setActiveGroup(group) {
  const stored = parseStoredUser() || {}
  const updated = {
    ...stored,
    role: group?.role || null,
    groupId: group?.id || null,
    groupName: group?.name || null,
  }
  localStorage.setItem(STORAGE_USER_KEY, JSON.stringify(updated))
  currentUser.value = updated
}

export function useAuth() {
  const router = useRouter()
  const { initPush } = usePushNotifications()

  const isAuthenticated = computed(
    () => !!currentUser.value && !!localStorage.getItem(STORAGE_TOKEN_KEY),
  )
  const isAdmin = computed(() => currentUser.value?.role === 'ADMIN')

  async function register(payload) {
    isLoading.value = true
    authError.value = null
    try {
      const data = await registerUser(payload)

      const userInfo = {
        id: data.user?.id || null,
        fullName: data.user?.fullName || data.user?.full_name || payload.fullName,
        email: data.user?.email || payload.email,
        role: null,
        groupId: null,
        groupName: null,
      }

      persistAuthSession(data.access_token, userInfo)
      initPush()
      scheduleAfterRegistration()

      router.push('/group-setup')
    } catch (err) {
      authError.value =
        err.response?.status === 409
          ? 'User with this email already exists'
          : err.userMessage || 'Something went wrong. Please try again'
    } finally {
      isLoading.value = false
    }
  }

  async function login(credentials) {
    isLoading.value = true
    authError.value = null

    try {
      const data = await loginUser(credentials)
      localStorage.setItem(STORAGE_TOKEN_KEY, data.access_token)

      let groups = []
      try {
        groups = await fetchMyGroups()
      } catch {
        // групи необов'язкові — продовжуємо без них
      }

      const userInfo = {
        id: data.user?.id || null,
        fullName: data.user?.fullName || data.user?.full_name || '',
        email: data.user?.email || credentials.email,
        role: null,
        groupId: null,
        groupName: null,
      }
      persistAuthSession(data.access_token, userInfo)

      initPush()

      if (!Array.isArray(groups) || groups.length === 0) {
        router.push('/group-setup')
      } else if (groups.length === 1) {
        setActiveGroup(groups[0])
        router.push('/feed')
      } else {
        router.push({
          name: 'SelectGroup',
          state: { groups },
        })
      }
    } catch (err) {
      localStorage.removeItem(STORAGE_TOKEN_KEY)
      const status = err.response?.status
      if (status === 429) {
        authError.value = 'Too many attempts. Please try again in 15 minutes'
      } else {
        authError.value = 'Invalid email or password'
      }
    } finally {
      isLoading.value = false
    }
  }

  async function logout() {
    isLoading.value = true
    try {
      await logoutUser()
    } catch {
    } finally {
      localStorage.removeItem(STORAGE_TOKEN_KEY)
      currentUser.value = null
      isLoading.value = false
      router.push('/login')
    }
  }

  return {
    currentUser,
    isLoading,
    authError,
    isAuthenticated,
    isAdmin,
    register,
    login,
    logout,
    setActiveGroup,
  }
}
