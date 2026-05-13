import { ref, onMounted, onUnmounted } from 'vue'

/**
 * WebSocket-клієнт з auto-reconnect і ping/pong heartbeat.
 *
 * Endpoint: ws://localhost:8000/ws?token={JWT}
 *
 * Очікувані повідомлення:
 *   { type: 'new_transaction', transaction: {...} }
 *   { type: 'ping' }  // сервер може слати щоб тримати з'єднання
 */
export function useWebSocket({ onTransaction } = {}) {
  const isConnected = ref(false)
  const reconnectAttempts = ref(0)
  let ws = null
  let reconnectTimer = null
  let pingInterval = null

  const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'
  const ENABLED = import.meta.env.VITE_WS_ENABLED === 'true'

  function connect() {
    if (!ENABLED) {
      console.info('WebSocket disabled (VITE_WS_ENABLED != true)')
      return
    }

    const token = localStorage.getItem('accessToken')
    if (!token) return

    try {
      ws = new WebSocket(`${WS_URL}?token=${encodeURIComponent(token)}`)

      ws.onopen = () => {
        isConnected.value = true
        reconnectAttempts.value = 0
        console.info('WebSocket connected')

        // Heartbeat — кожні 30 сек шлемо ping
        pingInterval = setInterval(() => {
          if (ws?.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }))
          }
        }, 30000)
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (data.type === 'new_transaction' && data.transaction) {
            onTransaction?.(data.transaction)
          }
        } catch (err) {
          console.warn('WS message parse error:', err)
        }
      }

      ws.onclose = () => {
        isConnected.value = false
        clearInterval(pingInterval)
        scheduleReconnect()
      }

      ws.onerror = () => {
        // onclose спрацює автоматично — не дублюємо logic
      }
    } catch (err) {
      console.warn('WS connection failed:', err)
      scheduleReconnect()
    }
  }

  /**
   * Exponential backoff: 1s, 2s, 4s, 8s, max 30s.
   */
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
      ws.onclose = null // щоб не тригернути scheduleReconnect
      ws.close()
      ws = null
    }
    isConnected.value = false
  }

  onMounted(connect)
  onUnmounted(disconnect)

  return {
    isConnected,
    reconnectAttempts,
  }
}
