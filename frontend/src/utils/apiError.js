import t from '../locales/en'

const STATUS_FALLBACKS = t.errors.byStatus

/**
 * @param {*} error  Помилка axios (або будь-яка)
 * @param {string} [fallback]  Текст, якщо нічого конкретнішого не знайдено
 * @returns {string}
 */
export function getApiErrorMessage(error, fallback = t.errors.fallback) {
  if (!error?.response) {
    if (error?.code === 'ECONNABORTED') {
      return t.errors.timeout
    }
    return t.errors.network
  }

  const { status, data } = error.response

  const detail = data?.detail
  if (typeof detail === 'string' && detail.trim()) {
    return detail
  }
  if (Array.isArray(detail) && detail.length) {
    const msg = detail[0]?.msg
    if (msg) return msg.replace(/^Value error,\s*/i, '')
  }
  if (typeof data?.message === 'string' && data.message.trim()) {
    return data.message
  }

  return STATUS_FALLBACKS[status] || fallback
}
