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

export function applyServerBlock(key, retryAfterSeconds) {
  const seconds = Number(retryAfterSeconds)
  if (!Number.isFinite(seconds) || seconds <= 0) return
  const data = load(key)
  data.attempts = []
  data.blockedUntil = Date.now() + seconds * 1000
  save(key, data)
}

export function resetAttempts(key) {
  localStorage.removeItem(STORAGE_PREFIX + key)
}
