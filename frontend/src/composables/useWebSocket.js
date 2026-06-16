import { ref, onMounted, onUnmounted, watch, toValue } from 'vue'

export function useWebSocket({ groupId, onTransaction, onReaction, onRequest } = {}) {
  const isConnected = ref(false)
  const reconnectAttempts = ref(0)
  let ws = null
  let reconnectTimer = null
  let pingInterval = null

  const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000/ws/feed'
  const ENABLED = import.meta.env.VITE_WS_ENABLED === 'true'

  function connect() {
    if (!ENABLED) {
      return
    }

    const gid = toValue(groupId)
    if (!gid) {
      return
    }

    try {
      ws = new WebSocket(`${WS_BASE_URL}/${gid}`)

      ws.onopen = () => {
        isConnected.value = true
        reconnectAttempts.value = 0

        pingInterval = setInterval(() => {
          if (ws?.readyState === WebSocket.OPEN) {
            ws.send('ping')
          }
        }, 30000)
      }

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data)
          if (msg.event === 'new_transaction') {
            onTransaction?.(msg.data)
          } else if (msg.event === 'reaction_updated') {
            onReaction?.(msg.data)
          } else if (msg.event === 'new_request' || msg.event === 'request_updated') {
            onRequest?.(msg.data, msg.event)
          }
        } catch {
          // Невалідний JSON у WS-повідомленні — ігноруємо
        }
      }

      ws.onclose = () => {
        isConnected.value = false
        if (pingInterval) {
          clearInterval(pingInterval)
          pingInterval = null
        }
        scheduleReconnect()
      }

      ws.onerror = () => {}
    } catch {
      // Не вдалося відкрити з'єднання — плануємо повторну спробу
      scheduleReconnect()
    }
  }

  function scheduleReconnect() {
    if (reconnectTimer) return
    const delay = Math.min(1000 * 2 ** reconnectAttempts.value, 30000)
    reconnectAttempts.value += 1
    reconnectTimer = setTimeout(() => {
      reconnectTimer = null
      connect()
    }, delay)
  }

  function disconnect() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    if (pingInterval) {
      clearInterval(pingInterval)
      pingInterval = null
    }
    if (ws) {
      ws.onclose = null
      ws.close()
      ws = null
    }
    isConnected.value = false
  }

  onMounted(() => {
    if (typeof groupId === 'function') {
      watch(
        () => toValue(groupId),
        (gid) => {
          if (gid && !ws) connect()
        },
        { immediate: true },
      )
    } else if (groupId) {
      connect()
    }
  })

  onUnmounted(disconnect)

  return {
    isConnected,
    reconnectAttempts,
  }
}
