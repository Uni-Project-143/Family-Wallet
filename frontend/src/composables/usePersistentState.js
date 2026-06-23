import { ref, watch } from 'vue'

/**
 * @param {string} key — ключ у localStorage
 * @param {*} defaultValue — fallback якщо нічого не збережено
 * @returns {import('vue').Ref}
 */
export function usePersistentState(key, defaultValue) {
  let initial = defaultValue
  try {
    const stored = localStorage.getItem(key)
    if (stored !== null) {
      initial = JSON.parse(stored)
    }
  } catch {
    // битий JSON — default
  }

  const state = ref(initial)

  watch(
    state,
    (newVal) => {
      try {
        localStorage.setItem(key, JSON.stringify(newVal))
      } catch {
        // localStorage недоступний (приватний режим / перевищено квоту) — ігноруємо
      }
    },
    { deep: true },
  )

  return state
}
