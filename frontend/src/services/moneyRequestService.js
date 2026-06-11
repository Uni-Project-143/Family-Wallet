import apiClient from './apiClient'

/**
 * @param {{ recipient_id: string, amount: number|string, description?: string|null }} payload
 * @returns {Promise<{ status: string, request_id: string, message: string }>}
 */
export async function createMoneyRequest({ recipient_id, amount, description = null }) {
  const response = await apiClient.post('/api/v1/requests/', {
    recipient_id,
    amount: String(amount),
    description,
  })
  return response.data
}

/**
 * @param {'PENDING'|'ACCEPTED'|'DECLINED'} status
 * @returns {Promise<Array<{id, requester_id, recipient_id, group_id, amount, description, status, created_at}>>}
 */
export async function fetchIncomingRequests(status = 'PENDING') {
  const response = await apiClient.get(`/api/v1/requests/incoming?status=${status}`)
  return response.data
}

/**
 * @returns {Promise<Array<{id, requester_id, recipient_id, amount, description, status, created_at}>>}
 */
export async function fetchOutgoingRequests() {
  const response = await apiClient.get('/api/v1/requests/outgoing')
  return response.data
}

/**
 * @param {string} requestId
 * @param {'ACCEPTED'|'DECLINED'} status
 * @param {string|null} fromCardId
 */
export async function respondToMoneyRequest(requestId, status, fromCardId = null) {
  const body = { status }
  if (fromCardId) body.from_card_id = fromCardId
  const response = await apiClient.patch(`/api/v1/requests/${requestId}`, body)
  return response.data
}
