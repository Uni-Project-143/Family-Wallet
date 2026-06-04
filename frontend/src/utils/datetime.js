/**
 * Парсить дату/час, отриману з бекенду, у коректний Date.
 *
 * Mongo/Beanie часто віддає НАЇВНИЙ UTC без позначки таймзони
 * (напр. "2026-06-03T22:14:00"). Без 'Z' / зсуву JavaScript трактує такий
 * рядок як ЛОКАЛЬНИЙ час, через що дата «з'їжджає» на величину таймзони.
 *
 * Рішення: якщо в рядку немає таймзони — додаємо 'Z' (трактуємо як UTC).
 *
 * @param {string|Date|null|undefined} value
 * @returns {Date|null}
 */
export function parseServerDate(value) {
  if (!value) return null
  if (value instanceof Date) return value
  const str = String(value)
  const hasTz = /([zZ])$|[+-]\d{2}:?\d{2}$/.test(str)
  const d = new Date(hasTz ? str : `${str}Z`)
  return Number.isNaN(d.getTime()) ? null : d
}
