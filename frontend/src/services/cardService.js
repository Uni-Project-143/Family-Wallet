import apiClient from './apiClient'

/**
 * Підключити картку Monobank.
 * POST /api/v1/monobank/connect
 *
 * Бекенд:
 * 1. Перевіряє членство юзера у групі (403 якщо ні)
 * 2. Валідує токен через GET https://api.monobank.ua/personal/client-info
 * 3. Перевіряє унікальність account_id (409 якщо вже підключено)
 * 4. Шифрує токен AES-256-GCM
 * 5. Реєструє webhook у Monobank
 * 6. Зберігає BankCard у БД
 *
 * @param {string} groupId
 * @param {string} personalToken
 * @returns {Promise<{ id: string, masked_pan: string, status: string, message: string }>}
 */
export async function connectMonobankCard(groupId, personalToken) {
  const response = await apiClient.post('/api/v1/monobank/connect', {
    group_id: groupId,
    personal_token: personalToken,
  })
  return response.data
}

/**
 * Відключити картку (hard delete на беку).
 * DELETE /api/v1/monobank/card/{card_id}
 *
 * Бекенд:
 * 1. Знаходить картку (404 якщо немає)
 * 2. Перевіряє що картка належить юзеру (403 якщо ні)
 * 3. Скидає webhook у Monobank API
 * 4. Видаляє запис з БД
 *
 * @param {string} cardId
 * @returns {Promise<{ message: string }>}
 */
export async function disconnectMonobankCard(cardId) {
  const response = await apiClient.delete(`/api/v1/monobank/card/${cardId}`)
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
