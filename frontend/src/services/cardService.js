import apiClient from './apiClient'

/**
 * Підключити картку Monobank.
 * POST /api/v1/monobank/connect
 *
 * Бекенд:
 * 1. Валідує токен через GET https://api.monobank.ua/personal/client-info
 * 2. Реєструє webhook через POST https://api.monobank.ua/personal/webhook
 * 3. Шифрує токен AES-256 і зберігає у БД
 *
 * @param {object} payload
 * @param {string} payload.groupId
 * @param {string} payload.apiToken
 * @param {string} [payload.alias]
 * @returns {Promise<{id, masked_pan, status, bank_name, balance}>}
 */
export async function connectMonobankCard(payload) {
  const response = await apiClient.post('/api/v1/monobank/connect', {
    group_id: payload.groupId,
    api_token: payload.apiToken,
    alias: payload.alias || null,
  })
  return response.data
}

/**
 * Список карток групи.
 * GET /api/v1/monobank/cards/{group_id}
 *
 * @param {string} groupId
 * @param {string} [status] — 'active' | 'inactive' | 'all' (default 'active')
 */
export async function fetchConnectedCards(groupId, status = 'active') {
  const response = await apiClient.get(`/api/v1/monobank/cards/${groupId}`, {
    params: { status },
  })
  return response.data
}

/**
 * Soft-delete картки. Транзакції залишаються.
 * DELETE /api/v1/monobank/card/{card_id}
 */
export async function disconnectMonobankCard(cardId) {
  const response = await apiClient.delete(`/api/v1/monobank/card/${cardId}`)
  return response.data
}
