import apiClient from './apiClient'

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
 * POST /api/v1/gift/{id}/invite — генерує invite link для запрошення донорів (PROJ-57).
 * @returns {Promise<{invite_url: string, token: string, expires_at?: string}>}
 */
export async function generateGiftInviteLink(giftId) {
  const response = await apiClient.post(`/api/v1/gift/${giftId}/invite`)
  return response.data
}

/**
 * GET /api/v1/gift/group/{group_id} — список gift events групи.
 * Бек виключає події де я target і unlock_date > now (PROJ-58).
 */
export async function fetchGroupGiftEvents(groupId) {
  const response = await apiClient.get(`/api/v1/gift/group/${groupId}`)
  return response.data
}
