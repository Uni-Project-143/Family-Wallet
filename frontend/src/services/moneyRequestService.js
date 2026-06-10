import apiClient from './apiClient'

/**
 * Запити коштів між учасниками групи (Money Requests).
 * Префікс беку: /api/v1/requests
 */

/**
 * Створити запит коштів (я прошу гроші у recipient).
 * POST /api/v1/requests/
 * @param {{ recipient_id: string, amount: number|string, description?: string|null }} payload
 * @returns {Promise<{ status: string, request_id: string, message: string }>}
 */
export async function createMoneyRequest({ recipient_id, amount, description = null }) {
  const response = await apiClient.post('/api/v1/requests/', {
    recipient_id,
    amount: String(amount), // на беку Decimal — передаємо рядком для точності
    description,
  })
  return response.data
}

/**
 * Вхідні запити до поточного користувача.
 * GET /api/v1/requests/incoming?status=PENDING
 * @param {'PENDING'|'ACCEPTED'|'DECLINED'} status
 * @returns {Promise<Array<{id, requester_id, recipient_id, group_id, amount, description, status, created_at}>>}
 */
export async function fetchIncomingRequests(status = 'PENDING') {
  const response = await apiClient.get(`/api/v1/requests/incoming?status=${status}`)
  return response.data
}

/**
 * Вихідні запити поточного користувача (всі статуси) — щоб показати відповідь
 * відправнику, навіть якщо він був офлайн у момент рішення отримувача.
 * GET /api/v1/requests/outgoing
 * @returns {Promise<Array<{id, requester_id, recipient_id, amount, description, status, created_at}>>}
 */
export async function fetchOutgoingRequests() {
  const response = await apiClient.get('/api/v1/requests/outgoing')
  return response.data
}

/**
 * Відповісти на запит (прийняти/відхилити). ACCEPTED → бек виконує віртуальний переказ.
 * PATCH /api/v1/requests/{requestId}
 * @param {string} requestId
 * @param {'ACCEPTED'|'DECLINED'} status
 */
export async function respondToMoneyRequest(requestId, status) {
  const response = await apiClient.patch(`/api/v1/requests/${requestId}`, { status })
  return response.data
}
