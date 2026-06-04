import apiClient from './apiClient'

/**
 * PUT /api/v1/auth/me/fcm-token — привʼязує FCM-токен пристрою до профілю,
 * щоб backend міг надсилати цьому користувачу push-сповіщення.
 *
 * Потребує Bearer-токен (додається автоматично в apiClient).
 *
 * @param {string} fcmToken
 * @returns {Promise<{success: boolean, message: string}>}
 */
export async function updateFcmToken(fcmToken) {
  const response = await apiClient.put('/api/v1/auth/me/fcm-token', {
    fcm_token: fcmToken,
  })
  return response.data
}
