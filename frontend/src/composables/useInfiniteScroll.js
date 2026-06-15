import { onUnmounted, ref, watch, toValue } from 'vue'

/**
 * Викликає callback коли sentinel-елемент потрапляє у viewport.
 * Використовується для infinite scroll на дні списку.
 *
 * Повертає sentinelRef — присвой його через ref="sentinelRef" на елемент,
 * який має бути спостережений (зазвичай div у кінці списку).
 *
 * IntersectionObserver створюється лише коли sentinel реально присутній
 * у DOM — це важливо при condition rendering (skeleton -> список).
 *
 * @param {Function} callback
 * @param {{ rootMargin?: string, threshold?: number }} [options]
 * @returns {{ sentinelRef: import('vue').Ref<HTMLElement|null> }}
 */
export function useInfiniteScroll(callback, options = {}) {
  const sentinelRef = ref(null)
  let observer = null

  watch(
    sentinelRef,
    (el, prevEl) => {
      if (observer && prevEl) observer.unobserve(prevEl)

      if (!el) return

      if (!observer) {
        observer = new IntersectionObserver(
          (entries) => {
            if (entries[0]?.isIntersecting) callback()
          },
          {
            // Якщо контент прокручується всередині елемента (а не вікна) — root
            // має бути цим елементом, інакше rootMargin не спрацьовує і догрузка
            // не тригериться. Передається через options.root (ref або елемент).
            root: toValue(options.root) || null,
            rootMargin: options.rootMargin || '200px',
            threshold: options.threshold || 0,
          },
        )
      }
      observer.observe(el)
    },
    { immediate: true },
  )

  onUnmounted(() => {
    if (observer) observer.disconnect()
  })

  return { sentinelRef }
}
