import apiClient from './apiClient'

/**
 * @param {object} payload - { name, target_user_id, unlock_date (ISO UTC), goal_amount, group_id }
 * @returns {Promise<{gift_id: string, status: string, ...}>}
 */
export async function createGiftEvent(payload) {
  const response = await apiClient.post('/api/v1/gift/create', payload)
  return response.data
}

export async function fetchGiftEventDetails(giftId) {
  const response = await apiClient.get(`/api/v1/gift/${giftId}/details`)
  return response.data
}

/**
 * POST /api/v1/gift/join — приєднатися до Secret Gift за invite-лінкою.
 * Бек витягує токен з лінки, валідує і повертає { gift_id, group_id, gift_name }.
 * @param {string} inviteLink — повна лінка або токен (бек бере останній сегмент)
 * @returns {Promise<{ message: string, gift_id: string, group_id: string, gift_name: string }>}
 */
export async function joinGiftByInvite(inviteLink) {
  const response = await apiClient.post('/api/v1/gift/join', { invite_link: inviteLink })
  return response.data
}

/**
 * @param {string} giftId
 * @returns {Promise<{invite_url: string, token: string}>}
 */
export async function generateGiftInviteLink(giftId) {
  const response = await apiClient.post(`/api/v1/gift/${giftId}/invite`)
  return response.data
}

/**
 * @param {string} groupId
 * @returns {Promise<Array<{id, name, target_user_id, target_user_name, unlock_date, goal_amount, collected_amount, status}>>}
 */
export async function fetchGroupGiftEvents(groupId) {
  const response = await apiClient.get(`/api/v1/gift/group/${groupId}`)
  return response.data
}

/**
 * @param {string} giftId
 * @param {{amount: number, card_id: string}} payload
 * @returns {Promise<{success: boolean, new_collected_amount: number}>}
 */
export async function contributeToGift(giftId, payload) {
  const response = await apiClient.post(`/api/v1/gift/${giftId}/contribute`, payload)
  return response.data
}
