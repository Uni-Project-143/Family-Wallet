import apiClient from './apiClient'

/**
 * Список транзакцій групи з фільтрами і сортуванням.
 * GET /api/v1/transactions/group/{group_id}?...filters
 *
 * Призначений для сторінки детального перегляду транзакцій
 * з фільтрацією за категорією, типом, сумою, датами.
 *
 * @param {string} groupId
 * @param {object} filters
 * @returns {Promise<{items, total, page, size, pages}>}
 */
export async function fetchGroupTransactions(groupId, filters = {}) {
  const params = new URLSearchParams()

  if (filters.category_id) params.set('category_id', filters.category_id)
  if (filters.tx_type) params.set('tx_type', filters.tx_type)
  if (filters.min_amount != null) params.set('min_amount', filters.min_amount)
  if (filters.max_amount != null) params.set('max_amount', filters.max_amount)
  if (filters.start_date) params.set('start_date', filters.start_date)
  if (filters.end_date) params.set('end_date', filters.end_date)

  params.set('sort_by', filters.sort_by || 'timestamp')
  params.set('sort_order', filters.sort_order || 'desc')
  params.set('page', filters.page || 1)
  params.set('size', filters.size || 20)

  const response = await apiClient.get(`/api/v1/transactions/group/${groupId}?${params.toString()}`)
  return response.data
}
export async function fetchFeed(groupId, page = 1, limit = 20) {
  const params = new URLSearchParams({ page, limit })
  const response = await apiClient.get(`/api/v1/feed/${groupId}?${params.toString()}`)
  return response.data
}

/**
 * Створює віртуальний переказ між картками сімейної групи.
 * POST /api/v1/transactions/transfer
 *
 * @param {object} payload
 * @param {string} payload.from_card_id
 * @param {string} payload.to_card_id
 * @param {string|number} payload.amount — сума (буде серіалізована як Decimal на беку)
 * @param {string|null} payload.description
 * @param {string|null} payload.category_id
 * @returns {Promise<{transfer_id, debit_transaction_id, credit_transaction_id, amount, from_effective_balance, to_effective_balance}>}
 */
/**
 * Поставити / зняти емодзі-реакцію на транзакцію (UPSERT + TOGGLE на беку).
 * POST /api/v1/transactions/{transactionId}/react
 *
 * Повторний клік по тому самому емодзі знімає реакцію (toggle вирішує бек).
 * @param {string} transactionId
 * @param {string} emoji
 * @returns {Promise<{ status: string, total_count: number, grouped_reactions: Record<string, number> }>}
 */
export async function reactToTransaction(transactionId, emoji) {
  const response = await apiClient.post(`/api/v1/transactions/${transactionId}/react`, { emoji })
  return response.data
}

export async function createTransfer({
  from_card_id,
  to_card_id,
  amount,
  description = null,
  category_id = null,
}) {
  const response = await apiClient.post('/api/v1/transactions/transfer', {
    from_card_id,
    to_card_id,
    amount: String(amount),
    description,
    category_id,
  })
  return response.data
}
