import apiClient from './apiClient'

/**
 * @param {string} fcmToken
 * @returns {Promise<{success: boolean, message: string}>}
 */
export async function updateFcmToken(fcmToken) {
  const response = await apiClient.put('/api/v1/auth/me/fcm-token', {
    fcm_token: fcmToken,
  })
  return response.data
}

/**
 * @returns {Promise<Array<{ _id?, id?, gift_id, notification_type, is_read, created_at }>>}
 */
export async function fetchNotifications() {
  const response = await apiClient.get('/api/v1/notifications/')
  return response.data
}

/**
 * @returns {Promise<{ status: string, modified_count: number }>}
 */
export async function markNotificationsRead() {
  const response = await apiClient.patch('/api/v1/notifications/mark-read')
  return response.data
}
