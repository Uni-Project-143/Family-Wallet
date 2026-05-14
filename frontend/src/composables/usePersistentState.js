import { ref, watch } from 'vue'

/**
 * Реактивне значення, синхронізоване з localStorage.
 * При F5 — значення відновлюється. При зміні — записується у LS.
 *
 * @param {string} key — ключ у localStorage
 * @param {*} defaultValue — fallback якщо нічого не збережено
 * @returns {import('vue').Ref}
 */
export function usePersistentState(key, defaultValue) {
  // Спроба прочитати збережене значення
  let initial = defaultValue
  try {
    const stored = localStorage.getItem(key)
    if (stored !== null) {
      initial = JSON.parse(stored)
    }
  } catch {
    // Битий JSON — використовуємо default
  }

  const state = ref(initial)

  // Автоматично зберігаємо при кожній зміні
  watch(
    state,
    (newVal) => {
      try {
        localStorage.setItem(key, JSON.stringify(newVal))
      } catch (err) {
        console.warn(`Failed to persist ${key}:`, err)
      }
    },
    { deep: true },
  )

  return state
}
