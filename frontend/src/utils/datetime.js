/**
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
