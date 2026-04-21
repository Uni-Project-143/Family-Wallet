import apiClient from './apiClient'

/**
 * Реєстрація нового користувача.
 * @param {{ fullName: string, email: string, password: string }} payload
 * @returns {Promise<{ token: string, user: object }>}
 */
export async function registerUser(payload) {
  const response = await apiClient.post('/auth/register', payload)
  return response.data
}

/**
 * Авторизація користувача.
 * @param {{ email: string, password: string }} credentials
 * @returns {Promise<{ token: string, user: object }>}
 */
export async function loginUser(credentials) {
  const response = await apiClient.post('/auth/login', credentials)
  return response.data
}

/**
 * Відправка листа для скидання паролю.
 * @param {{ email: string }} payload
 * @returns {Promise<{ message: string }>}
 */
export async function requestPasswordReset(payload) {
  const response = await apiClient.post('/auth/forgot-password', payload)
  return response.data
}

/**
 * Отримання invite-лінку групи (тільки для Admin).
 * @returns {Promise<{ inviteUrl: string, expiresAt: string }>}
 */
export async function fetchGroupInviteLink() {
  const response = await apiClient.get('/group/invite')
  return response.data
}

/**
 * Перегенерація invite-лінку (старий стає недійсним).
 * @returns {Promise<{ inviteUrl: string, expiresAt: string }>}
 */
export async function regenerateGroupInviteLink() {
  const response = await apiClient.post('/group/invite/regenerate')
  return response.data
}
