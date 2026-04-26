import apiClient from './apiClient'

/**
 * Реєстрація — POST /api/v1/auth/register
 * Swagger schema: { email, password, fullName }
 * confirmPassword НЕ відправляємо — перевіряється лише на фронті
 * @param {{ fullName, email, password }} payload
 * @returns {{ access_token, token_type }}
 */
export async function registerUser(payload) {
  const response = await apiClient.post('/api/v1/auth/register', {
    fullName: payload.fullName,
    email: payload.email,
    password: payload.password,
    confirmPassword: payload.password, // ← додаю цей рядок
  })
  return response.data
}

/**
 * Авторизація — POST /api/v1/auth/login
 * @param {{ email, password }} credentials
 * @returns {{ access_token, token_type }}
 */
export async function loginUser(credentials) {
  const response = await apiClient.post('/api/v1/auth/login', {
    email: credentials.email,
    password: credentials.password,
  })
  return response.data
}

/**
 * Створення групи — POST /api/v1/groups
 * Swagger schema: { name }
 * @param {{ name }} payload
 * @returns {{ group_id, name, message }}
 */
export async function createGroup(payload) {
  const response = await apiClient.post('/api/v1/group', {
    name: payload.name,
  })
  return response.data
}

/**
 * Мої групи — GET /api/v1/groups
 * @returns {{ groups: [] }}
 */
export async function fetchMyGroups() {
  const response = await apiClient.get('/api/v1/group')
  return response.data
}

/**
 * Invite link — GET /api/v1/groups/{id}/invite
 * @param {string} groupId
 * @returns {{ invite_link, token, expires_at }}
 */
export async function fetchGroupInviteLink(groupId) {
  const response = await apiClient.get(`/api/v1/group/${groupId}/invite`)
  return response.data
}

/**
 * Перегенерація invite link — POST /api/v1/group/{group_id}/invite/regenerate
 * @param {string} groupId
 * @returns {{ invite_link, token, expires_at }}
 */
export async function regenerateGroupInviteLink(groupId) {
  const response = await apiClient.post(`/api/v1/group/${groupId}/invite/regenerate`)
  return response.data
}

/**
 * Приєднання до групи — POST /api/v1/group/join
 * @param {{ invite_link }} payload
 * @returns {{ message }}
 */
export async function joinGroup(payload) {
  const response = await apiClient.post(`/api/v1/group/join`, {
    invite_link: payload.inviteLink,
  })
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
