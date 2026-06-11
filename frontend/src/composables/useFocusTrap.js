import { onUnmounted, watch } from 'vue'

/**
 * Focus trap для модальних вікон.
 * - Робить #app inert поки модалка відкрита (Tab не виходить з модалки)
 * - Зберігає попередній focus і відновлює його при закритті
 * - Циклить Tab всередині модалки (з останнього елемента — на перший)
 *
 * @param {Ref<HTMLElement|null>} rootRef — ref на корневий елемент модалки
 * @param {() => boolean} isActive — getter, що повертає чи відкрита модалка
 */
export function useFocusTrap(rootRef, isActive) {
  let previousFocus = null

  function getFocusableElements() {
    if (!rootRef.value) return []
    const selectors = 'a[href], button, input, textarea, select, [tabindex]:not([tabindex="-1"])'
    return Array.from(rootRef.value.querySelectorAll(selectors)).filter(
      (el) => !el.disabled && !el.hidden && el.offsetParent !== null,
    )
  }

  function onKeydown(e) {
    if (e.key !== 'Tab') return
    const focusable = getFocusableElements()
    if (focusable.length === 0) {
      e.preventDefault()
      return
    }

    const first = focusable[0]
    const last = focusable[focusable.length - 1]

    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault()
      last.focus()
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault()
      first.focus()
    }
  }

  function activate() {
    previousFocus = document.activeElement
    document.getElementById('app')?.setAttribute('inert', '')

    setTimeout(() => {
      const focusable = getFocusableElements()
      focusable[0]?.focus()
    }, 60)

    document.addEventListener('keydown', onKeydown)
  }

  function deactivate() {
    document.getElementById('app')?.removeAttribute('inert')
    document.removeEventListener('keydown', onKeydown)
    if (previousFocus && typeof previousFocus.focus === 'function') {
      previousFocus.focus()
    }
    previousFocus = null
  }

  watch(isActive, (active) => {
    if (active) activate()
    else deactivate()
  })

  onUnmounted(() => {
    deactivate()
  })
}
