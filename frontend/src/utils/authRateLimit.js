/**
 * Локальний rate-limit для login/register форм.
 *
 * УВАГА: це UX-надбудова, не безпека. Атакуючий обходить через curl/Postman
 * за 5 секунд. Реальний rate-limit має бути на беку (slowapi з лічником
 * тільки невдалих спроб per-email).
 *
 * Правила: 5 невдалих спроб у вікні 5 хв → блок на 15 хв.
 */

const MAX_ATTEMPTS = 5
const WINDOW_MS = 5 * 60 * 1000
const BLOCK_MS = 15 * 60 * 1000
const STORAGE_PREFIX = 'authRateLimit:'

function load(key) {
  try {
    const raw = localStorage.getItem(STORAGE_PREFIX + key)
    if (!raw) return { attempts: [], blockedUntil: null }
    return JSON.parse(raw)
  } catch {
    return { attempts: [], blockedUntil: null }
  }
}

function save(key, data) {
  localStorage.setItem(STORAGE_PREFIX + key, JSON.stringify(data))
}

/**
 * Записує невдалу спробу. Якщо у вікні WINDOW_MS накопичилось MAX_ATTEMPTS — ставимо блок.
 */
export function recordFailedAttempt(key) {
  const now = Date.now()
  const data = load(key)
  data.attempts = data.attempts.filter((t) => now - t < WINDOW_MS)
  data.attempts.push(now)
  if (data.attempts.length >= MAX_ATTEMPTS) {
    data.blockedUntil = now + BLOCK_MS
  }
  save(key, data)
}

/**
 * @returns {boolean} true якщо форма зараз заблокована
 */
export function isBlocked(key) {
  const data = load(key)
  if (!data.blockedUntil) return false
  if (Date.now() >= data.blockedUntil) {
    resetAttempts(key)
    return false
  }
  return true
}

/**
 * @returns {number} мілісекунди до зняття блоку (0 якщо блоку нема)
 */
export function getRemainingBlockMs(key) {
  const data = load(key)
  if (!data.blockedUntil) return 0
  return Math.max(0, data.blockedUntil - Date.now())
}

export function resetAttempts(key) {
  localStorage.removeItem(STORAGE_PREFIX + key)
}
