import { computed } from 'vue'
import { usePersistentState } from './usePersistentState'

/**
 * Емодзі-реакції на транзакціях (Telegram-style).
 *
 * Backend наразі не має ендпоінта для збереження реакцій, тому реакція
 * поточного користувача зберігається локально у localStorage і "накладається"
 * поверх базових реакцій, які приходять з /api/v1/feed (transaction.reactions).
 *
 * Модель: один користувач — одна реакція на транзакцію (як базовий режим
 * у Telegram). Повторний клік по тій самій емодзі знімає реакцію.
 */

const STORAGE_KEY = 'fw_tx_reactions'

// 7 найбільш базових реакцій
export const REACTION_EMOJIS = ['👍', '❤️', '😂', '🔥', '😮', '😢', '🙏']

// Singleton-стан, спільний для всіх карток транзакцій.
// Формат: { [transactionId]: '🔥' }
const myReactions = usePersistentState(STORAGE_KEY, {})

export function useReactions() {
  /**
   * Реакція поточного користувача на транзакцію (або null).
   * @param {string|number} txId
   */
  function getMyReaction(txId) {
    return myReactions.value[txId] || null
  }

  /**
   * Поставити / зняти реакцію. Якщо вже стоїть та сама — знімаємо,
   * інакше — замінюємо на нову.
   * @param {string|number} txId
   * @param {string} emoji
   */
  function toggleReaction(txId, emoji) {
    const next = { ...myReactions.value }
    if (next[txId] === emoji) {
      delete next[txId]
    } else {
      next[txId] = emoji
    }
    myReactions.value = next
  }

  return { myReactions, getMyReaction, toggleReaction }
}

/**
 * Обчислює підсумковий список реакцій для відображення:
 * базові реакції з бекенду + накладена реакція поточного користувача.
 *
 * @param {() => object} txGetter — getter, що повертає transaction
 * @returns {import('vue').ComputedRef<Array<{emoji:string,count:number,mine:boolean}>>}
 */
export function useDisplayReactions(txGetter) {
  const { getMyReaction } = useReactions()

  return computed(() => {
    const tx = txGetter()
    const base = (tx?.reactions || []).map((r) => ({
      emoji: r.emoji,
      count: r.count,
      mine: false,
    }))

    const mine = getMyReaction(tx?.id)
    if (!mine) return base

    const existing = base.find((r) => r.emoji === mine)
    if (existing) {
      existing.count += 1
      existing.mine = true
      return base
    }
    return [...base, { emoji: mine, count: 1, mine: true }]
  })
}
