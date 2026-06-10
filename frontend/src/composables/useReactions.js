import { reactive, computed } from 'vue'
import { usePersistentState } from './usePersistentState'
import { reactToTransaction } from '../services/transactionService'

/**
 * Емодзі-реакції на транзакціях (Telegram-style), підключені до бекенду.
 *
 * Контракт беку:
 *  - POST /api/v1/transactions/{id}/react { emoji } — UPSERT + TOGGLE
 *    (повторний клік по своєму ж емодзі видаляє реакцію). Відповідь містить
 *    grouped_reactions: { "👍": 2, "❤️": 1 } — згруповані лічильники.
 *  - WebSocket подія "reaction_updated" з тим самим grouped_reactions —
 *    щоб усі учасники групи бачили зміни в реальному часі.
 *
 * Джерело істини щодо ЛІЧИЛЬНИКІВ — сервер (groupedReactions).
 * Локально (localStorage) тримаємо лише ВЛАСНИЙ емодзі на транзакцію, бо
 * стрічка /feed наразі не повертає, яка саме реакція належить поточному юзеру.
 */

const STORAGE_KEY = 'fw_tx_reactions'

// 7 базових реакцій
export const REACTION_EMOJIS = ['👍', '❤️', '😂', '🔥', '😮', '😢', '🙏']

// Моя реакція на транзакцію: { [txId]: '🔥' } — переживає reload.
const myReactions = usePersistentState(STORAGE_KEY, {})

// Серверні згруповані лічильники: { [txId]: { '👍': 2, '❤️': 1 } }
const groupedReactions = reactive({})

/** Записати власну реакцію (або прибрати, якщо emoji порожній). */
function setMyReaction(txId, emoji) {
  const next = { ...myReactions.value }
  if (emoji) next[txId] = emoji
  else delete next[txId]
  myReactions.value = next
}

/**
 * Застосувати серверні згруповані лічильники для транзакції.
 * Викликається з відповіді POST і з WebSocket-події "reaction_updated".
 */
export function applyServerReactions(txId, grouped) {
  if (!txId) return
  groupedReactions[txId] = grouped && typeof grouped === 'object' ? { ...grouped } : {}
}

/**
 * Початковий засів реакцій з елемента стрічки (/feed повертає `reactions` +
 * `my_reaction`). Сіємо лише ОДИН раз на транзакцію — щоб не перетерти
 * пізніші живі оновлення (POST/WS) застарілим знімком зі стрічки.
 */
export function seedReactions(tx) {
  if (!tx?.id) return
  if (groupedReactions[tx.id] !== undefined) return // вже маємо актуальні дані
  groupedReactions[tx.id] =
    tx.reactions && typeof tx.reactions === 'object' ? { ...tx.reactions } : {}
  // my_reaction із сервера авторитетне (перекриває localStorage).
  if ('my_reaction' in tx) setMyReaction(tx.id, tx.my_reaction || null)
}

export function useReactions() {
  /** Реакція поточного користувача на транзакцію (або null). */
  function getMyReaction(txId) {
    return myReactions.value[txId] || null
  }

  /**
   * Поставити / зняти реакцію. Оптимістично оновлюємо UI, потім синхронізуємо
   * з відповіддю беку (toggle/upsert вирішує бек за user_id).
   */
  async function toggleReaction(txId, emoji) {
    if (!txId || !emoji) return

    const prevMine = myReactions.value[txId] || null
    const prevGrouped = { ...(groupedReactions[txId] || {}) }

    // ── Оптимістичне оновлення ──
    const g = { ...prevGrouped }
    if (prevMine && g[prevMine]) {
      g[prevMine] -= 1
      if (g[prevMine] <= 0) delete g[prevMine]
    }
    let nextMine
    if (prevMine === emoji) {
      nextMine = null // повторний клік по своєму емодзі — знімаємо
    } else {
      nextMine = emoji
      g[emoji] = (g[emoji] || 0) + 1
    }
    setMyReaction(txId, nextMine)
    groupedReactions[txId] = g

    // ── Синхронізація з беком ──
    try {
      const res = await reactToTransaction(txId, emoji)
      if (res && res.grouped_reactions) {
        groupedReactions[txId] = { ...res.grouped_reactions }
      }
    } catch {
      // Відкат при помилці
      setMyReaction(txId, prevMine)
      groupedReactions[txId] = prevGrouped
    }
  }

  return { myReactions, getMyReaction, toggleReaction, applyServerReactions }
}

/**
 * Підсумковий список реакцій для відображення: { emoji, count, mine }.
 * Лічильники — серверні (groupedReactions), «мій» емодзі підсвічуємо за myReactions.
 *
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

    // Поки немає серверних даних (стрічка /feed їх не віддає) — показуємо
    // хоча б власну реакцію, щоб вона не зникала до першого оновлення з беку.
    if (mineEmoji) {
      return [{ emoji: mineEmoji, count: 1, mine: true }]
    }
    return []
  })
}
