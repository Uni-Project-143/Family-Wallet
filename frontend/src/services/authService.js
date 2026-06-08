import apiClient from './apiClient'
import { scheduleAfterJoin } from '../utils/cardReminder'

/**
 * Реєстрація.
 * POST /api/v1/auth/register
 */
export async function registerUser(payload) {
  const response = await apiClient.post('/api/v1/auth/register', {
    fullName: payload.fullName,
    email: payload.email,
    password: payload.password,
    confirmPassword: payload.confirmPassword,
  })
  return response.data
}

/**
 * Логін.
 * POST /api/v1/auth/login
 * @returns {{ access_token: string, token_type: string }}
 */
export async function loginUser(credentials) {
  const response = await apiClient.post('/api/v1/auth/login', {
    email: credentials.email,
    password: credentials.password,
  })
  return response.data
}

/**
 * Список груп поточного юзера.
 * GET /api/v1/group/me
 * @returns {Promise<Array<{id: string, name: string, role: 'ADMIN'|'MEMBER'}>>}
 */
export async function fetchMyGroups() {
  const response = await apiClient.get('/api/v1/group/me')
  return response.data
}

/**
 * Generate / get active invite link.
 * GET /api/v1/group/{groupId}/invite
 */
export async function fetchGroupInviteLink(groupId) {
  const response = await apiClient.get(`/api/v1/group/${groupId}/invite`)
  return response.data
}

/**
 * Regenerate invite link (old links invalidated).
 * POST /api/v1/group/{groupId}/invite/regenerate
 */
export async function regenerateGroupInviteLink(groupId) {
  const response = await apiClient.post(`/api/v1/group/${groupId}/invite/regenerate`)
  return response.data
}

/**
 * Створити групу.
 * POST /api/v1/group/
 */
export async function createGroup(name) {
  const response = await apiClient.post('/api/v1/group/', { name })
  scheduleAfterJoin()
  return response.data
}

/**
 * Приєднатись до групи за invite-лінком.
 * POST /api/v1/group/join
 */
export async function joinGroup(inviteLink) {
  const response = await apiClient.post('/api/v1/group/join', {
    invite_link: inviteLink, // ← snake_case, як чекає бек
  })
  scheduleAfterJoin()
  return response.data
}
/**
 * Запит на скидання паролю — POST /api/v1/auth/forgot-password
 * @param {{ email: string }} payload
 * @returns {{ message: string }}
 */
export async function requestPasswordReset(payload) {
  const response = await apiClient.post('/api/v1/auth/forgot-password', {
    email: payload.email,
  })
  return response.data
}

/**
 * Встановлення нового пароля за токеном з email-лінки.
 * POST /api/v1/auth/reset-password
 * @param {{ token: string, new_password: string }} payload
 * @returns {{ message: string }}
 */
export async function resetPassword(payload) {
  const response = await apiClient.post('/api/v1/auth/reset-password', {
    token: payload.token,
    new_password: payload.new_password,
  })
  return response.data
}
// /**
//  * Список учасників групи.
//  * GET /api/v1/group/{group_id}/members
//  */
// export async function fetchGroupMembers(groupId) {
//   const response = await apiClient.get(`/api/v1/group/${groupId}/members`)
//   return response.data
// }
export async function fetchGroupMembers(groupId) {
  try {
    const response = await apiClient.get(`/api/v1/group/${groupId}/members`)
    return response.data
  } catch (err) {
    if (err.response?.status === 404) {
      // endpoint поки не реалізований — повертаємо порожній масив
      return []
    }
    throw err
  }
}
/**
 * Logout — додає поточний JWT токен у чорний список на беку.
 * POST /api/v1/auth/logout
 *
 * Бекенд читає токен з заголовку Authorization (apiClient додає автоматично),
 * додає його у колекцію blacklisted_tokens — після цього токен стає невалідним.
 *
 * @returns {Promise<{ message: string }>}
 */
export async function logoutUser() {
  const response = await apiClient.post('/api/v1/auth/logout')
  return response.data
}
