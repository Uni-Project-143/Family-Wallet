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
      const data = await registerUser({
        fullName: formPayload.fullName,
        email: formPayload.email,
        password: formPayload.password,
        // confirmPassword НЕ відправляємо — Swagger його не очікує
      })

      // Зберігаємо токен (access_token — саме така назва поля зі Swagger)
      localStorage.setItem('accessToken', data.access_token)

      // Зберігаємо базові дані юзера — groupId отримаємо після GroupSetup
      const userInfo = {
        fullName: formPayload.fullName,
        email: formPayload.email,
        role: null,
        groupId: null,
        groupName: null,
      }
      localStorage.setItem('currentUser', JSON.stringify(userInfo))
      currentUser.value = userInfo

      router.push('/group-setup')
    } catch (err) {
      // Бекенд повертає { timestamp, errorCode, message }
      const message = err.response?.data?.message
      const status = err.response?.status

      if (status === 409) {
        authError.value = 'User with this email already exists'
      } else if (status === 422) {
        // Pydantic validation error — беремо перше повідомлення
        const detail = err.response?.data?.detail
        if (Array.isArray(detail) && detail.length > 0) {
          authError.value = detail[0].msg
        } else {
          authError.value = 'Please check the correctness of the entered data'
        }
      } else {
        authError.value = message || 'Something went wrong. Please try again'
      }
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
      const data = await loginUser(credentials)

      localStorage.setItem('accessToken', data.access_token)

      // Після логіну потрібно отримати групи юзера
      // Поки зберігаємо мінімум — групи підтягнемо у FeedView
      const userInfo = {
        email: credentials.email,
        fullName: '',
        role: null,
        groupId: null,
        groupName: null,
      }
      localStorage.setItem('currentUser', JSON.stringify(userInfo))
      currentUser.value = userInfo

      router.push('/feed')
    } catch (err) {
      const status = err.response?.status
      if (status === 429) {
        authError.value = 'Too many login attempts. Please try again later.'
      } else {
        // 401 — навмисно одне повідомлення (захист від user enumeration)
        authError.value = 'Incorrect email or password. Please try again.'
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
    if (status === 409) return 'User with this email already exists'
    if (status === 400) return 'Please check the correctness of the entered data'

    return 'Something went wrong. Please try again'
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
