import apiClient from './apiClient'

/**
 * Список транзакцій поточного юзера.
 * GET /api/v1/transactions/?filters
 *
 * Поки бек не має endpoint /transactions/group/{id}, використовуємо особистий.
 * Коли з'явиться group endpoint — замінити URL.
 *
 * @param {object} filters
 * @param {string} [filters.category_id]
 * @param {'INCOME'|'EXPENSE'} [filters.tx_type]
 * @param {number} [filters.min_amount]
 * @param {number} [filters.max_amount]
 * @param {string} [filters.start_date]  YYYY-MM-DD
 * @param {string} [filters.end_date]    YYYY-MM-DD
 * @param {'amount'|'timestamp'|'category_id'} [filters.sort_by='timestamp']
 * @param {'asc'|'desc'} [filters.sort_order='desc']
 * @param {number} [filters.page=1]
 * @param {number} [filters.size=20]
 * @returns {Promise<{items, total, page, size, pages}>}
 */
export async function fetchMyTransactions(filters = {}) {
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

  const response = await apiClient.get(`/api/v1/transactions/?${params.toString()}`)
  return response.data
}
