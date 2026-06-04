/**
 * Єдина точка перетворення помилки API → змістовне повідомлення для користувача.
 *
 * Витягує конкретний текст із відповіді бекенду (FastAPI: поле `detail`),
 * коректно обробляє валідацію 422 (`detail` = масив `{loc, msg}`),
 * мережеві помилки/таймаути та дає осмислені фолбеки за HTTP-кодом
 * замість загального "Something went wrong".
 */

import t from '../locales/en'

// Фолбеки за HTTP-кодом беруться з локалі (єдине джерело істини).
const STATUS_FALLBACKS = t.errors.byStatus

/**
 * @param {*} error  Помилка axios (або будь-яка)
 * @param {string} [fallback]  Текст, якщо нічого конкретнішого не знайдено
 * @returns {string}
 */
export function getApiErrorMessage(error, fallback = t.errors.fallback) {
  // 1. Немає відповіді — мережа / таймаут / CORS / сервер лежить
  if (!error?.response) {
    if (error?.code === 'ECONNABORTED') {
      return t.errors.timeout
    }
    return t.errors.network
  }

  const { status, data } = error.response

  // 2. Конкретне повідомлення з бекенду (FastAPI → `detail`)
  const detail = data?.detail
  if (typeof detail === 'string' && detail.trim()) {
    return detail
  }
  // 422 / валідація: detail — масив { loc, msg }
  if (Array.isArray(detail) && detail.length) {
    const msg = detail[0]?.msg
    if (msg) return msg.replace(/^Value error,\s*/i, '')
  }
  // Деякі ендпоінти повертають `message`
  if (typeof data?.message === 'string' && data.message.trim()) {
    return data.message
  }

  // 3. Фолбек за статусом
  return STATUS_FALLBACKS[status] || fallback
}
