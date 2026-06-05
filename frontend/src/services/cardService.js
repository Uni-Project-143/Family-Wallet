import apiClient from './apiClient'
import { scheduleAfterDisconnect } from '../utils/cardReminder'

/**
 * Step 1: отримати список карток Monobank за API token.
 * Бек обмеження: 1 запит на 60 секунд.
 */
export async function fetchMonobankCards(personalToken) {
  const response = await apiClient.post('/api/v1/monobank/client-info', {
    personal_token: personalToken,
  })
  return response.data
}

/**
 * Step 2: підключити обрану картку до групи.
 */
export async function connectMonobankCard(groupId, personalToken, card) {
  const response = await apiClient.post('/api/v1/monobank/connect', {
    group_id: groupId,
    personal_token: personalToken,
    account_id: card.account_id,
    masked_pan: card.masked_pan,
    balance: card.balance,
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
  scheduleAfterDisconnect() // після disconnect — reminder через 5 хв
  return response.data
}
/**
 * Список карток усіх учасників групи.
 * GET /api/v1/bank-cards/group/{group_id}
 *
 * Бек повертає всі картки групи без encrypted_token (це поле приховане).
 * Доступно будь-якому учаснику групи.
 *
 * @param {string} groupId
 * @returns {Promise<Array<{id, user_id, group_id, account_id, masked_pan, balance, effective_balance, virtual_balance, status, transaction_ids, owner_full_name}>>}
 */
export async function fetchGroupCards(groupId) {
  const response = await apiClient.get(`/api/v1/bank-cards/group/${groupId}`)
  return response.data
}
