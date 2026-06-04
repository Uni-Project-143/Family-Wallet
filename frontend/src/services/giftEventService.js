import apiClient from './apiClient'

//Service-шар з 4-ма API-функціями

/**
 * POST /api/v1/gift/create — створює нову gift event (PROJ-55, PROJ-56).
 * @param {object} payload - { name, target_user_id, unlock_date (ISO UTC), goal_amount, group_id }
 * @returns {Promise<{gift_id: string, status: string, ...}>}
 */
export async function createGiftEvent(payload) {
  const response = await apiClient.post('/api/v1/gift/create', payload)
  return response.data
}

/**
 * GET /api/v1/gift/{id}/details — деталі події (PROJ-58, PROJ-64).
 * Target user отримує 403 до unlock_date (бек middleware).
 */
export async function fetchGiftEventDetails(giftId) {
  const response = await apiClient.get(`/api/v1/gift/${giftId}/details`)
  return response.data
}

/**
 * POST /api/v1/gift/{id}/invite — генерує invite-лінк для запрошення донорів (PROJ-57).
 * Тільки організатор (інакше 403). Повторний виклик повертає той самий активний token.
 *
 * @param {string} giftId
 * @returns {Promise<{invite_url: string, token: string}>}
 */
export async function generateGiftInviteLink(giftId) {
  const response = await apiClient.post(`/api/v1/gift/${giftId}/invite`)
  return response.data
}

/**
 * GET /api/v1/gift/group/{group_id} — список активних подій групи.
 * Бек виключає події, де я target і unlock_date ще не настав (PROJ-58 ізоляція).
 *
 * @param {string} groupId
 * @returns {Promise<Array<{id, name, target_user_id, target_user_name, unlock_date, goal_amount, collected_amount, status}>>}
 */
export async function fetchGroupGiftEvents(groupId) {
  const response = await apiClient.get(`/api/v1/gift/group/${groupId}`)
  return response.data
}

/**
 * POST /api/v1/gift/{id}/contribute — внесок до збору.
 * Створює secret-транзакцію (−amount) з картки користувача й оновлює зібрану суму.
 *
 * Валідації беку: збір ACTIVE і ще не минув, не target, 0 < amount ≤ 100000,
 * картка належить користувачу, користувач — у групі.
 *
 * @param {string} giftId
 * @param {{amount: number, card_id: string}} payload
 * @returns {Promise<{success: boolean, new_collected_amount: number}>}
 */
export async function contributeToGift(giftId, payload) {
  const response = await apiClient.post(`/api/v1/gift/${giftId}/contribute`, payload)
  return response.data
}
