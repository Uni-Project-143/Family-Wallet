import { onMounted, onUnmounted, ref } from 'vue'

/**
 * Викликає callback коли sentinel-елемент потрапляє у viewport.
 * Використовується для infinite scroll на дні списку.
<<<<<<< Updated upstream
 *
 * Повертає sentinelRef — присвой його через ref="sentinelRef" на елемент,
 * який має бути спостережений (зазвичай div у кінці списку).
 *
 * @param {Function} callback
 * @param {{ rootMargin?: string, threshold?: number }} [options]
 * @returns {{ sentinelRef: import('vue').Ref<HTMLElement|null> }}
=======
>>>>>>> Stashed changes
 */
export function useInfiniteScroll(callback, options = {}) {
  const sentinelRef = ref(null)
  let observer = null

  onMounted(() => {
    observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) {
          callback()
        }
      },
      {
        rootMargin: options.rootMargin || '200px',
        threshold: options.threshold || 0,
      },
    )

    if (sentinelRef.value) {
      observer.observe(sentinelRef.value)
    }
  })

  onUnmounted(() => {
    if (observer) observer.disconnect()
  })

  return { sentinelRef }
}
