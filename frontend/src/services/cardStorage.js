/**
 * Локальний кеш підключених карток.
 *
 * TODO: коли бекенд додасть GET /api/v1/monobank/cards/{groupId},
 * замінити цей кеш на запит з беку. UI залишиться той самий.
 */

const STORAGE_KEY_PREFIX = 'monobankCards:'

function getKey(groupId) {
  return `${STORAGE_KEY_PREFIX}${groupId}`
}

/**
 * Список карток для конкретної групи.
 * @param {string} groupId
 * @returns {Array<{id, masked_pan, status, alias?}>}
 */
export function getCardsFromStorage(groupId) {
  if (!groupId) return []
  try {
    const raw = localStorage.getItem(getKey(groupId))
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

/**
 * Додає картку у кеш групи.
 */
export function addCardToStorage(groupId, card) {
  if (!groupId) return
  const cards = getCardsFromStorage(groupId)
  // Уникаємо дублікатів за id
  const filtered = cards.filter((c) => c.id !== card.id)
  filtered.push(card)
  localStorage.setItem(getKey(groupId), JSON.stringify(filtered))
}

/**
 * Прибирає картку з кешу за id.
 */
export function removeCardFromStorage(groupId, cardId) {
  if (!groupId) return
  const cards = getCardsFromStorage(groupId).filter((c) => c.id !== cardId)
  localStorage.setItem(getKey(groupId), JSON.stringify(cards))
}
