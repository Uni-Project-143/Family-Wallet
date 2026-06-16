import { onUnmounted, ref, watch, toValue } from 'vue'

/**
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
