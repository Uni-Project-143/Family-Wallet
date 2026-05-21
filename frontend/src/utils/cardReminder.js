const STORAGE_KEY = 'cardReminderScheduledAt'

const FIVE_MIN_MS = 5 * 60 * 1000
const THIRTY_MIN_MS = 30 * 60 * 1000

function setSchedule(deltaMs) {
  const triggerAt = Date.now() + deltaMs
  localStorage.setItem(STORAGE_KEY, String(triggerAt))
}

export function scheduleAfterRegistration() {
  setSchedule(FIVE_MIN_MS)
}

export function scheduleAfterDisconnect() {
  setSchedule(FIVE_MIN_MS)
}

export function scheduleAfterJoin() {
  setSchedule(FIVE_MIN_MS)
}

export function scheduleLater() {
  setSchedule(THIRTY_MIN_MS)
}

export function dismissForever() {
  localStorage.removeItem(STORAGE_KEY)
}

/**
 * @returns {number | null} Unix-timestamp коли треба показати модалку, або null
 */
export function getScheduledTime() {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) return null
  const num = Number(raw)
  return Number.isFinite(num) ? num : null
}
