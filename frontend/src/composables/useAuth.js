import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { registerUser, loginUser, fetchMyGroups } from '../services/authService'

/**
 * Composable для управління станом авторизації.
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

  const isAuthenticated = computed(() => !!localStorage.getItem('accessToken'))
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
   * Реєстрація — після успіху редирект на /group-setup.
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
        confirmPassword: formPayload.password,
      })

      const userInfo = {
        fullName: formPayload.fullName,
        email: formPayload.email,
        role: null,
        groupId: null,
        groupName: null,
      }

      persistAuthSession(data.access_token, userInfo)
      router.push('/group-setup')
    } catch (err) {
      const status = err.response?.status
      const message = err.response?.data?.message

      if (status === 409) {
        authError.value = 'Користувач з таким email вже існує'
      } else if (status === 422) {
        const detail = err.response?.data?.detail
        if (Array.isArray(detail) && detail.length > 0) {
          authError.value = detail[0].msg
        } else {
          authError.value = 'Перевірте правильність введених даних'
        }
      } else {
        authError.value = message || 'Щось пішло не так. Спробуйте ще раз'
      }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Авторизація — підтягує групи після логіну.
   * Якщо група є → /feed, якщо немає → /group-setup.
   * @param {{ email: string, password: string }} credentials
   */
  async function login(credentials) {
    isLoading.value = true
    authError.value = null
    try {
      const data = await loginUser(credentials)

      // Зберігаємо токен одразу — він потрібен для fetchMyGroups
      localStorage.setItem('accessToken', data.access_token)

      let userInfo = {
        email: credentials.email,
        fullName: '',
        role: null,
        groupId: null,
        groupName: null,
      }

      try {
        const groupsData = await fetchMyGroups()

        // Підтримуємо обидва формати відповіді бекенду:
        // { groups: [...] } або просто [...]
        const groups = Array.isArray(groupsData) ? groupsData : groupsData.groups

        if (groups && groups.length > 0) {
          const firstGroup = groups[0]
          userInfo.role = firstGroup.role
          userInfo.groupId = firstGroup.group_id
          userInfo.groupName = firstGroup.name
          persistAuthSession(data.access_token, userInfo)
          router.push('/feed')
        } else {
          // Акаунт є але групи немає
          persistAuthSession(data.access_token, userInfo)
          router.push('/group-setup')
        }
      } catch {
        // fetchMyGroups впав — зберігаємо мінімум і йдемо на group-setup
        persistAuthSession(data.access_token, userInfo)
        router.push('/group-setup')
      }
    } catch (err) {
      // Очищаємо токен якщо логін не вдався
      localStorage.removeItem('accessToken')

      const status = err.response?.status
      if (status === 429) {
        authError.value = 'Забагато спроб. Спробуйте через 15 хв'
      } else {
        // 401 — навмисно одне повідомлення (захист від user enumeration)
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
