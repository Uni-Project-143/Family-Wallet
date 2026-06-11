export const CATEGORY_PALETTE = [
  '#C4862A',
  '#4A6FA5',
  '#5A8A6A',
  '#C4613A',
  '#8A7AAA',
  '#3E8E8E',
  '#B5894A',
  '#9A5BA5',
  '#6E8B3D',
  '#C2557A',
]

const NEUTRAL_COLOR = '#9C8F7A'

const NAMED_COLORS = {
  продукти: '#C4862A',
  'продукти та їжа': '#C4862A',
  їжа: '#C4862A',
  food: '#C4862A',
  'food & groceries': '#C4862A',
  groceries: '#C4862A',
  транспорт: '#4A6FA5',
  transport: '#4A6FA5',
  travel: '#4A6FA5',
  аптека: '#5A8A6A',
  здоровʼя: '#5A8A6A',
  "здоров'я": '#5A8A6A',
  pharmacy: '#5A8A6A',
  health: '#5A8A6A',
  кафе: '#C4613A',
  'кафе та ресторани': '#C4613A',
  ресторани: '#C4613A',
  cafe: '#C4613A',
  restaurants: '#C4613A',
  розваги: '#8A7AAA',
  entertainment: '#8A7AAA',
  подарунки: '#C2557A',
  gifts: '#C2557A',
  перекази: '#3E8E8E',
  переказ: '#3E8E8E',
  transfer: '#3E8E8E',
  transfers: '#3E8E8E',
  інше: NEUTRAL_COLOR,
  other: NEUTRAL_COLOR,
}

function hashString(str) {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = (hash << 5) - hash + str.charCodeAt(i)
    hash |= 0
  }
  return Math.abs(hash)
}

/**
 * Основний колір категорії за її назвою.
 * @param {string} name
 * @returns {string} hex-колір
 */
export function getCategoryColor(name) {
  const key = (name || '').toString().trim().toLowerCase()
  if (!key) return NEUTRAL_COLOR
  if (NAMED_COLORS[key]) return NAMED_COLORS[key]
  return CATEGORY_PALETTE[hashString(key) % CATEGORY_PALETTE.length]
}

export function hexToRgba(hex, alpha = 1) {
  const clean = hex.replace('#', '')
  const r = parseInt(clean.slice(0, 2), 16)
  const g = parseInt(clean.slice(2, 4), 16)
  const b = parseInt(clean.slice(4, 6), 16)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

export function badgeStyleFromColor(color) {
  return {
    color,
    background: hexToRgba(color, 0.12),
    borderColor: hexToRgba(color, 0.32),
  }
}

/**
 * Готовий набір стилів для бейджа категорії за НАЗВОЮ.
 * @param {string} name
 */
export function getCategoryBadgeStyle(name) {
  return badgeStyleFromColor(getCategoryColor(name))
}

export const CATEGORY_BY_SLUG = {
  groceries: { label: 'Продукти', emoji: '🛒', color: '#C4862A' },
  fast_food: { label: 'Кафе та ресторани', emoji: '🍔', color: '#C4613A' },
  pharmacy: { label: 'Аптека', emoji: '💊', color: '#5A8A6A' },
  entertainment: { label: 'Розваги', emoji: '🎬', color: '#8A7AAA' },
  transport: { label: 'Транспорт', emoji: '🚗', color: '#4A6FA5' },
  gifts: { label: 'Подарунки', emoji: '🎁', color: '#C2557A' },
  gift_contribution: { label: 'Подарунок', emoji: '🎁', color: '#C2557A' },
  transfer: { label: 'Перекази', emoji: '💸', color: '#3E8E8E' },
  other: { label: 'Інше', emoji: '💰', color: NEUTRAL_COLOR },
}

/**
 * @param {object} tx — елемент стрічки
 */
export function resolveCategory(tx) {
  if (!tx) return { ...CATEGORY_BY_SLUG.other }

  const slug = (tx.category_code ?? tx.category_slug ?? tx.category_id ?? '')
    .toString()
    .trim()
    .toLowerCase()

  if (slug && CATEGORY_BY_SLUG[slug]) {
    return CATEGORY_BY_SLUG[slug]
  }

  const name = tx.category_name || 'Інше'
  return {
    label: name,
    emoji: tx.category_emoji || '💰',
    color: getCategoryColor(name),
  }
}
