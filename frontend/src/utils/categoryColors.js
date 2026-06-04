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

/** Набір стилів бейджа (фон/рамка/текст) із готового hex-кольору. */
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

/**
 * Словник slug-категорій від бекенду (контракт із бекендером).
 * Бек віддає код категорії (groceries / fast_food / pharmacy / ...),
 * а фронт мапить його у людську назву, емодзі та колір.
 *
 * ⚠️ Працює лише якщо стрічка /api/v1/feed РЕАЛЬНО віддає цей код
 * (поле category_code / category_slug / category_id). Зараз feed віддає
 * вже резолвлену category_name="Інше", тож слаг сюди не доходить — це
 * фіксується на боці беку (1 рядок: прокинути tx.category_id у відповідь).
 */
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
 * Єдина точка визначення відображення категорії для транзакції.
 * Повертає { label, emoji, color }.
 *
 * Пріоритет:
 *  1. slug-код від беку (category_code / category_slug / category_id),
 *     якщо він є у словнику CATEGORY_BY_SLUG;
 *  2. інакше — резолв за назвою category_name (поточна поведінка стрічки).
 *
 * Завдяки цьому, щойно бек почне віддавати slug, категорії одразу стануть
 * правильними — без додаткових змін на фронті.
 *
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

  // Fallback: резолв за назвою (як зараз віддає feed).
  const name = tx.category_name || 'Інше'
  return {
    label: name,
    emoji: tx.category_emoji || '💰',
    color: getCategoryColor(name),
  }
}
