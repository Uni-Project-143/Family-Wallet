import { ref, computed } from 'vue'
import { fetchMyTransactions } from '../services/transactionService'

/**
 * Стрічка транзакцій з пагінацією та infinite scroll.
 *
 * TODO: коли бек додасть GET /api/v1/transactions/group/{group_id} —
 * замінити fetchMyTransactions на fetchGroupTransactions(groupId, filters)
 */
export function useFeedTransactions(groupId) {
  const transactions = ref([])
  const isLoading = ref(false)
  const isLoadingMore = ref(false)
  const error = ref(null)

  const currentPage = ref(1)
  const totalPages = ref(1)
  const totalCount = ref(0)

  const hasMore = computed(() => currentPage.value < totalPages.value)

  /**
   * Завантажити першу сторінку (replace).
   */
  async function loadFirstPage(filters = {}) {
    isLoading.value = true
    error.value = null
    currentPage.value = 1

    try {
      const data = await fetchMyTransactions({
        ...filters,
        page: 1,
        size: 20,
      })
      transactions.value = data.items
      totalPages.value = data.pages
      totalCount.value = data.total
    } catch (err) {
      error.value = err
      transactions.value = []
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Завантажити наступну сторінку (append) — для infinite scroll.
   */
  async function loadMore(filters = {}) {
    if (!hasMore.value || isLoadingMore.value) return

    isLoadingMore.value = true
    const nextPage = currentPage.value + 1

    try {
      const data = await fetchMyTransactions({
        ...filters,
        page: nextPage,
        size: 20,
      })
      transactions.value.push(...data.items)
      currentPage.value = nextPage
      totalPages.value = data.pages
    } catch (err) {
      error.value = err
    } finally {
      isLoadingMore.value = false
    }
  }

  /**
   * Додати транзакцію на початок стрічки (для WebSocket push).
   */
  function prependTransaction(tx) {
    // Захист від дублікатів — якщо webhook прийшов після API запиту
    if (transactions.value.some((t) => t.id === tx.id)) return
    transactions.value.unshift(tx)
    totalCount.value += 1
  }

  return {
    transactions,
    isLoading,
    isLoadingMore,
    error,
    currentPage,
    totalPages,
    totalCount,
    hasMore,
    loadFirstPage,
    loadMore,
    prependTransaction,
  }
}
