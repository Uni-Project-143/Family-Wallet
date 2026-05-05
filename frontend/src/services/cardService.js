import apiClient from './apiClient'

/**
 * Підключити картку Monobank.
 * POST /api/v1/monobank/connect
 *
 * Бекенд (monobank_service.connect_card):
 * 1. Перевіряє членство юзера у групі
 * 2. Валідує токен через GET https://api.monobank.ua/personal/client-info
 * 3. Перевіряє унікальність account_id (унеможливлює подвійне підключення)
 * 4. Шифрує токен AES-256-GCM
 * 5. Реєструє webhook у Monobank
 * 6. Зберігає BankCard у БД
 *
 * @param {object} payload
 * @param {string} payload.groupId
 * @param {string} payload.personalToken
 * @returns {Promise<{ masked_pan: string, status: string, message: string }>}
 */
export async function connectMonobankCard(payload) {
  const response = await apiClient.post('/api/v1/monobank/connect', {
    group_id: payload.groupId,
    personal_token: payload.personalToken,
  })
  return response.data
}

// /**
//  * Список карток групи.
//  * GET /api/v1/monobank/cards/{group_id}
//  *
//  * @param {string} groupId
//  * @param {string} [status] — 'active' | 'inactive' | 'all' (default 'active')
//  */
// export async function fetchConnectedCards(groupId, status = 'active') {
//   const response = await apiClient.get(`/api/v1/monobank/cards/${groupId}`, {
//     params: { status },
//   })
//   return response.data
// }

// /**
//  * Soft-delete картки. Транзакції залишаються.
//  * DELETE /api/v1/monobank/card/{card_id}
//  */
// export async function disconnectMonobankCard(cardId) {
//   const response = await apiClient.delete(`/api/v1/monobank/card/${cardId}`)
//   return response.data
// }
