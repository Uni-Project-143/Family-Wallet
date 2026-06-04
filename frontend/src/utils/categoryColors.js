/**
 * Стабільні кольори категорій транзакцій.
 *
 * Мета: кожна категорія завжди має ОДИН і той самий колір — і в бейджі транзакції
 * (TransactionCard), і в донат-діаграмі "Spending by Category" (FeedView).
 * Раніше колір у діаграмі залежав від позиції в сортуванні за сумою, тому одна й та
 * сама категорія могла "стрибати" між кольорами. Тепер колір прив'язаний до НАЗВИ.
 *
 * Палітра узгоджена з Figma → "Category Chart Colors"
 * (Food / Transport / Pharmacy / Cafe / Other) і гармонує з золото-кремовою темою.
 */

// Базова палітра (порядок = Figma: gold, blue, green, terracotta, purple, ...)
export const CATEGORY_PALETTE = [
  '#C4862A', // amber / gold  — Food & Groceries
  '#4A6FA5', // blue          — Transport
  '#5A8A6A', // green         — Pharmacy / Health
  '#C4613A', // terracotta    — Cafe / Restaurants
  '#8A7AAA', // purple        — Other / Entertainment
  '#3E8E8E', // teal
  '#B5894A', // bronze
  '#9A5BA5', // magenta
  '#6E8B3D', // olive
  '#C2557A', // rose
]

// Нейтральний колір для "Інше / Other / без категорії"
const NEUTRAL_COLOR = '#9C8F7A'

/**
 * Явна прив'язка відомих назв категорій до кольорів — щоб ключові категорії
 * (продукти, транспорт, аптека, кафе) завжди збігалися з дизайн-системою,
 * незалежно від мови назви, що приходить з бекенду.
 */
const NAMED_COLORS = {
  // 🛒 Продукти / їжа
  продукти: '#C4862A',
  'продукти та їжа': '#C4862A',
  їжа: '#C4862A',
  food: '#C4862A',
  'food & groceries': '#C4862A',
  groceries: '#C4862A',
  // 🚌 Транспорт
  транспорт: '#4A6FA5',
  transport: '#4A6FA5',
  travel: '#4A6FA5',
  // 💊 Аптека / здоров'я
  аптека: '#5A8A6A',
  здоровʼя: '#5A8A6A',
  "здоров'я": '#5A8A6A',
  pharmacy: '#5A8A6A',
  health: '#5A8A6A',
  // ☕ Кафе / ресторани
  кафе: '#C4613A',
  'кафе та ресторани': '#C4613A',
  ресторани: '#C4613A',
  cafe: '#C4613A',
  restaurants: '#C4613A',
  // 🎬 Розваги
  розваги: '#8A7AAA',
  entertainment: '#8A7AAA',
  // 🎁 Подарунки
  подарунки: '#C2557A',
  gifts: '#C2557A',
  // 💸 Перекази
  перекази: '#3E8E8E',
  переказ: '#3E8E8E',
  transfer: '#3E8E8E',
  transfers: '#3E8E8E',
  // 💰 Інше / без категорії
  інше: NEUTRAL_COLOR,
  other: NEUTRAL_COLOR,
}

/** Детермінований хеш рядка → невід'ємне число (для стабільного вибору кольору). */
function hashString(str) {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = (hash << 5) - hash + str.charCodeAt(i)
    hash |= 0 // приводимо до 32-біт
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

/** hex → rgba з заданою прозорістю. */
export function hexToRgba(hex, alpha = 1) {
  const clean = hex.replace('#', '')
  const r = parseInt(clean.slice(0, 2), 16)
  const g = parseInt(clean.slice(2, 4), 16)
  const b = parseInt(clean.slice(4, 6), 16)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

/**
 * Готовий набір стилів для бейджа категорії: колір тексту, м'який фон і рамка
 * в одному тоні. Використовується через :style у TransactionCard.
 * @param {string} name
 */
export function getCategoryBadgeStyle(name) {
  const color = getCategoryColor(name)
  return {
    color,
    background: hexToRgba(color, 0.12),
    borderColor: hexToRgba(color, 0.32),
  }
}
