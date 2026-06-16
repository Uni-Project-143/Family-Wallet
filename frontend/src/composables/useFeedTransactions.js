import { ref } from 'vue'
import { fetchFeed } from '../services/transactionService'

const PAGE_SIZE = 20

/**
 * @param {string | (() => string|null|undefined)} groupIdSource
 */
export function useFeedTransactions(groupIdSource) {
  const transactions = ref([])
  const isLoading = ref(false)
  const isLoadingMore = ref(false)
  const error = ref(null)

  const currentPage = ref(1)
  const totalCount = ref(0)
  const hasMore = ref(false)

  function resolveGroupId() {
    return typeof groupIdSource === 'function' ? groupIdSource() : groupIdSource
  }

  async function loadFirstPage() {
    const gid = resolveGroupId()

    if (!gid) {
      transactions.value = []
      totalCount.value = 0
      hasMore.value = false
      return
    }

    isLoading.value = true
    error.value = null
    currentPage.value = 1

    try {
      const data = await fetchFeed(gid, 1, PAGE_SIZE)
      transactions.value = data.items
      totalCount.value = data.total
      hasMore.value = data.has_more
    } catch (err) {
      error.value = err
      transactions.value = []
      hasMore.value = false
    } finally {
      isLoading.value = false
    }
  }

  async function loadMore() {
    if (!hasMore.value || isLoadingMore.value) return

    const gid = resolveGroupId()
    if (!gid) return

    isLoadingMore.value = true
    const nextPage = currentPage.value + 1

    try {
      const data = await fetchFeed(gid, nextPage, PAGE_SIZE)
      transactions.value.push(...data.items)
      currentPage.value = nextPage
      hasMore.value = data.has_more
    } catch (err) {
      error.value = err
    } finally {
      isLoadingMore.value = false
    }
  }

  function prependTransaction(tx) {
    if (!tx?.id) return
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
    totalCount,
    hasMore,
    loadFirstPage,
    loadMore,
    prependTransaction,
  }
}
