import { reactive, computed } from 'vue'
import { usePersistentState } from './usePersistentState'
import { reactToTransaction } from '../services/transactionService'

const STORAGE_KEY = 'fw_tx_reactions'

export const REACTION_EMOJIS = ['👍', '❤️', '😂', '🔥', '😮', '😢', '🙏']

const myReactions = usePersistentState(STORAGE_KEY, {})

const groupedReactions = reactive({})

function setMyReaction(txId, emoji) {
  const next = { ...myReactions.value }
  if (emoji) next[txId] = emoji
  else delete next[txId]
  myReactions.value = next
}

export function applyServerReactions(txId, grouped) {
  if (!txId) return
  groupedReactions[txId] = grouped && typeof grouped === 'object' ? { ...grouped } : {}
}

export function seedReactions(tx) {
  if (!tx?.id) return
  if (groupedReactions[tx.id] !== undefined) return
  groupedReactions[tx.id] =
    tx.reactions && typeof tx.reactions === 'object' ? { ...tx.reactions } : {}
  if ('my_reaction' in tx) setMyReaction(tx.id, tx.my_reaction || null)
}

export function useReactions() {
  function getMyReaction(txId) {
    return myReactions.value[txId] || null
  }

  async function toggleReaction(txId, emoji) {
    if (!txId || !emoji) return

    const prevMine = myReactions.value[txId] || null
    const prevGrouped = { ...(groupedReactions[txId] || {}) }

    const g = { ...prevGrouped }
    if (prevMine && g[prevMine]) {
      g[prevMine] -= 1
      if (g[prevMine] <= 0) delete g[prevMine]
    }
    let nextMine
    if (prevMine === emoji) {
      nextMine = null
    } else {
      nextMine = emoji
      g[emoji] = (g[emoji] || 0) + 1
    }
    setMyReaction(txId, nextMine)
    groupedReactions[txId] = g

    try {
      const res = await reactToTransaction(txId, emoji)
      if (res && res.grouped_reactions) {
        groupedReactions[txId] = { ...res.grouped_reactions }
      }
    } catch {
      setMyReaction(txId, prevMine)
      groupedReactions[txId] = prevGrouped
    }
  }

  return { myReactions, getMyReaction, toggleReaction, applyServerReactions }
}

/**
 * @param {() => object} txGetter — getter, що повертає transaction
 */
export function useDisplayReactions(txGetter) {
  return computed(() => {
    const tx = txGetter()
    const txId = tx?.id
    if (!txId) return []

    const mineEmoji = myReactions.value[txId] || null
    const grouped = groupedReactions[txId]

    if (grouped && Object.keys(grouped).length) {
      return Object.entries(grouped).map(([emoji, count]) => ({
        emoji,
        count,
        mine: emoji === mineEmoji,
      }))
    }

    if (mineEmoji) {
      return [{ emoji: mineEmoji, count: 1, mine: true }]
    }
    return []
  })
}
