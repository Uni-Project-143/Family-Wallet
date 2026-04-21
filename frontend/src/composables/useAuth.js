import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { registerUser, loginUser } from '../services/authService'

/**
 * Composable для управління станом авторизації.
 * Зберігає JWT у localStorage та надає методи login/register.
 * @returns {{
 *   currentUser: import('vue').Ref,
 *   isAuthenticated: import('vue').ComputedRef<boolean>,
 *   isAdmin: import('vue').ComputedRef<boolean>,
 *   isLoading: import('vue').Ref<boolean>,
 *   authError: import('vue').Ref<string|null>,
 *   register: Function,
 *   login: Function,
 *   logout: Function,
 * }}
 */
export function useAuth() {
  const router = useRouter()

  const currentUser = ref(parseStoredUser())
  const isLoading = ref(false)
  const authError = ref(null)

  const isAuthenticated = computed(() => !!currentUser.value)
  const isAdmin = computed(() => currentUser.value?.role === 'ADMIN')

  /**
   * Зчитує збережений користувач з localStorage.
   * @returns {object|null}
   */
  function parseStoredUser() {
    try {
      const stored = localStorage.getItem('currentUser')
      return stored ? JSON.parse(stored) : null
    } catch {
      return null
    }
  }

  /**
   * Зберігає токен і дані користувача в localStorage.
   * @param {string} token
   * @param {object} user
   */
  function persistAuthSession(token, user) {
    localStorage.setItem('accessToken', token)
    localStorage.setItem('currentUser', JSON.stringify(user))
    currentUser.value = user
  }

  /**
   * Реєстрація нового користувача.
   * @param {{ fullName: string, email: string, password: string }} formPayload
   */
  async function register(formPayload) {
    isLoading.value = true
    authError.value = null
    try {
      // const { token, user } = await registerUser(formPayload)
      // persistAuthSession(token, user)
      // router.push('/group-setup')
      // ── MOCK — імітація відповіді сервера ──
      await new Promise((r) => setTimeout(r, 800)) // імітація затримки мережі

      const mockUser = {
        id: 'mock-user-1',
        fullName: formPayload.fullName,
        email: formPayload.email,
        role: null, // роль ще не визначена — визначиться у GroupSetup
        groupId: null, // група ще не створена
      }
      const mockToken = 'mock-jwt-token-' + Date.now()

      persistAuthSession(mockToken, mockUser)
      router.push('/group-setup')
      // ── кінець MOCK ──
    } catch (err) {
      authError.value = extractErrorMessage(err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Авторизація існуючого користувача.
   * @param {{ email: string, password: string }} credentials
   */
  async function login(credentials) {
    isLoading.value = true
    authError.value = null
    try {
      // const { token, user } = await loginUser(credentials)
      // persistAuthSession(token, user)
      // router.push('/feed')

      // ── MOCK ──
      await new Promise((r) => setTimeout(r, 600))

      const mockUser = {
        id: 'mock-user-1',
        fullName: 'Olena K.',
        email: credentials.email,
        role: 'ADMIN',
        groupId: 'mock-group-1',
      }
      const mockToken = 'mock-jwt-token-' + Date.now()

      persistAuthSession(mockToken, mockUser)
      router.push('/feed')
      // ── кінець MOCK ──
    } catch (err) {
      const status = err.response?.status
      if (status === 429) {
        authError.value = 'Забагато спроб. Спробуйте через 15 хв'
      } else {
        authError.value = 'Невірний email або пароль'
      }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Вихід із системи — очищення сесії.
   */
  function logout() {
    localStorage.removeItem('accessToken')
    localStorage.removeItem('currentUser')
    currentUser.value = null
    router.push('/login')
  }

  /**
   * Дістає зрозуміле повідомлення про помилку з axios error.
   * @param {Error} err
   * @returns {string}
   */
  function extractErrorMessage(err) {
    const serverMessage = err.response?.data?.message
    if (serverMessage) return serverMessage

    const status = err.response?.status
    if (status === 409) return 'Користувач з таким email вже існує'
    if (status === 400) return 'Перевірте правильність введених даних'

    return 'Щось пішло не так. Спробуйте ще раз'
  }

  return {
    currentUser,
    isAuthenticated,
    isAdmin,
    isLoading,
    authError,
    register,
    login,
    logout,
  }
}
