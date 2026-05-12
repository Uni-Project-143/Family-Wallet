// import { ref, computed } from 'vue'
// import { useRouter } from 'vue-router'
// import { loginUser, registerUser, fetchMyGroups } from '../services/authService'

// const STORAGE_TOKEN_KEY = 'accessToken'
// const STORAGE_USER_KEY = 'currentUser'

// function parseStoredUser() {
//   try {
//     const raw = localStorage.getItem(STORAGE_USER_KEY)
//     return raw ? JSON.parse(raw) : null
//   } catch {
//     return null
//   }
// }

// // Реактивний глобальний стан
// const currentUser = ref(parseStoredUser())
// const isLoading = ref(false)
// const authError = ref(null)

// function persistAuthSession(token, user) {
//   localStorage.setItem(STORAGE_TOKEN_KEY, token)
//   localStorage.setItem(STORAGE_USER_KEY, JSON.stringify(user))
//   currentUser.value = user
// }

// export function useAuth() {
//   const router = useRouter()

//   const isAuthenticated = computed(
//     () => !!currentUser.value && !!localStorage.getItem(STORAGE_TOKEN_KEY),
//   )
//   const isAdmin = computed(() => currentUser.value?.role === 'ADMIN')

//   /**
//    * Реєстрація нового юзера.
//    * Після реєстрації групи ще нема, тому відправляємо на /group-setup.
//    */
//   async function register(payload) {
//     isLoading.value = true
//     authError.value = null
//     try {
//       const data = await registerUser(payload)

//       const userInfo = {
//         fullName: payload.fullName,
//         email: payload.email,
//         role: null,
//         groupId: null,
//         groupName: null,
//       }

//       persistAuthSession(data.access_token, userInfo)
//       router.push('/group-setup')
//     } catch (err) {
//       const status = err.response?.status
//       if (status === 409) {
//         authError.value = 'Користувач з таким email вже існує'
//       } else if (status === 422) {
//         authError.value = err.response?.data?.detail?.[0]?.msg || 'Перевірте правильність полів'
//       } else {
//         authError.value = err.response?.data?.message || 'Щось пішло не так. Спробуйте ще раз'
//       }
//     } finally {
//       isLoading.value = false
//     }
//   }

//   /**
//    * Логін з повним flow:
//    * 1. POST /auth/login — отримуємо токен
//    * 2. Зберігаємо токен у localStorage (apiClient interceptor читає звідти)
//    * 3. GET /group/me — підтягуємо групи юзера з role і groupId
//    * 4. Беремо першу групу (MVP) → формуємо userInfo
//    * 5. Якщо є groupId → /feed; якщо груп нема → /group-setup
//    */
//   async function login(credentials) {
//     isLoading.value = true
//     authError.value = null

//     try {
//       // Крок 1: отримуємо токен
//       const tokenData = await loginUser(credentials)

//       // Крок 2: зберігаємо токен ДО fetchMyGroups,
//       // бо apiClient додасть його у Authorization header
//       localStorage.setItem(STORAGE_TOKEN_KEY, tokenData.access_token)

//       // Крок 3: підтягуємо групи з реального endpoint /group/me
//       let groups = []
//       try {
//         groups = await fetchMyGroups()
//       } catch (err) {
//         // Якщо ендпоінт впав — логін все ще працює, юзер піде на group-setup
//         console.warn('fetchMyGroups failed:', err)
//       }

//       // Крок 4: формуємо повний об'єкт юзера
//       const previousSession = parseStoredUser() || {}
//       let userInfo

//       if (Array.isArray(groups) && groups.length > 0) {
//         // Беремо першу групу — для MVP підтримуємо лише одну активну групу
//         const primaryGroup = groups[0]
//         userInfo = {
//           fullName: previousSession.fullName || '',
//           email: credentials.email,
//           role: primaryGroup.role, // 'ADMIN' або 'MEMBER' — з беку
//           groupId: primaryGroup.id, // справжній ID з беку
//           groupName: primaryGroup.name,
//         }
//       } else {
//         // Юзер без груп — наприклад, акаунт є, але не приєднався ні до якої сім'ї
//         userInfo = {
//           fullName: previousSession.fullName || '',
//           email: credentials.email,
//           role: null,
//           groupId: null,
//           groupName: null,
//         }
//       }

//       persistAuthSession(tokenData.access_token, userInfo)

//       // Крок 5: редирект за станом юзера
//       if (userInfo.groupId) {
//         router.push('/feed')
//       } else {
//         router.push('/group-setup')
//       }
//     } catch (err) {
//       // Логін фейл (401, 429, etc.) — токен не зберігаємо
//       localStorage.removeItem(STORAGE_TOKEN_KEY)

//       const status = err.response?.status
//       if (status === 429) {
//         authError.value = 'Забагато спроб. Спробуйте через 15 хв'
//       } else {
//         // 401 і будь-які інші — однаковий текст
//         // (захист від user enumeration з AC US 2)
//         authError.value = 'Невірний email або пароль'
//       }
//     } finally {
//       isLoading.value = false
//     }
//   }

//   /**
//    * Logout — видаляємо тільки токен.
//    * fullName/role/groupId залишаються у localStorage для UX наступного логіну.
//    */
//   function logout() {
//     localStorage.removeItem(STORAGE_TOKEN_KEY)
//     currentUser.value = null
//     router.push('/login')
//   }

//   return {
//     currentUser,
//     isLoading,
//     authError,
//     isAuthenticated,
//     isAdmin,
//     register,
//     login,
//     logout,
//   }
// }

import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { loginUser, registerUser, fetchMyGroups, logoutUser } from '../services/authService'

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
        fullName: data.user?.full_name || payload.fullName,
        email: data.user?.email || payload.email,
        role: null,
        groupId: null,
        groupName: null,
      }

      persistAuthSession(data.access_token, userInfo)
      router.push('/group-setup')
    } catch (err) {
      const status = err.response?.status
      if (status === 409) {
        authError.value = 'User with this email already exists'
      } else if (status === 422) {
        authError.value = err.response?.data?.detail?.[0]?.msg || 'Check the fields'
      } else {
        authError.value = 'Something went wrong. Please try again'
      }
    } finally {
      isLoading.value = false
    }
  }

  async function login(credentials) {
    isLoading.value = true
    authError.value = null

    try {
      // Крок 1: токен + дані юзера з бекенду
      const data = await loginUser(credentials)
      localStorage.setItem(STORAGE_TOKEN_KEY, data.access_token)

      // Крок 2: тягнемо групи
      let groups = []
      try {
        groups = await fetchMyGroups()
      } catch (err) {
        console.warn('fetchMyGroups failed:', err)
      }

      // Крок 3: зберігаємо БАЗОВУ інформацію юзера БЕЗ конкретної групи
      const userInfo = {
        id: data.user?.id || null,
        fullName: data.user?.full_name || '',
        email: data.user?.email || credentials.email,
        role: null,
        groupId: null,
        groupName: null,
      }
      persistAuthSession(data.access_token, userInfo)

      // Крок 4: маршрутизація залежно від кількості груп
      if (!Array.isArray(groups) || groups.length === 0) {
        // Немає груп — на створення/приєднання
        router.push('/group-setup')
      } else if (groups.length === 1) {
        // Одна група — авто-вибір, на feed
        setActiveGroup(groups[0])
        router.push('/feed')
      } else {
        // Кілька груп — юзер сам обирає
        // Передаємо список груп через router state (не зберігаємо в БД, бо це тимчасово)
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
        // 401 і інші — однакове повідомлення (захист від user enumeration)
        authError.value = 'Invalid email or password'
      }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Logout — повний flow:
   * 1. Викликаємо POST /auth/logout — бек додає токен у blacklist
   * 2. Чистимо локальний стан незалежно від результату беку
   * 3. Редирект на /login
   *
   * Якщо бек впав (network error, 5xx) — все одно вилогінюємо локально.
   * Інакше юзер застрягне у "залогіненому" стані з невалідним токеном.
   */
  async function logout() {
    isLoading.value = true
    try {
      await logoutUser()
    } catch (err) {
      // Логуємо, але не блокуємо логаут
      console.warn('Logout API failed:', err)
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
