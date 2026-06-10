import { ref, onMounted, onUnmounted, watch, toValue } from 'vue'

/**
 * WebSocket-клієнт з auto-reconnect і ping/pong heartbeat.
 *
 * Endpoint: ws://localhost:8000/ws/feed/{group_id}
 *
 * Очікувані повідомлення:
 *   { event: 'new_transaction', data: {...} }
 *   { event: 'reaction_updated', data: { transaction_id, grouped_reactions, ... } }
 *   { event: 'new_request' | 'request_updated', data: {...} }
 */
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
      console.info('WebSocket disabled (VITE_WS_ENABLED != true)')
      return
    }

    const gid = toValue(groupId)
    if (!gid) {
      console.info('WebSocket: no group_id yet, skipping connect')
      return
    }

    try {
      ws = new WebSocket(`${WS_BASE_URL}/${gid}`)

      ws.onopen = () => {
        isConnected.value = true
        reconnectAttempts.value = 0
        console.info(`WebSocket connected to group ${gid}`)

        // Heartbeat — кожні 30 сек шлемо ping (бек ігнорує payload, просто тримає з'єднання)
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
        } catch (err) {
          console.warn('WS message parse error:', err)
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

  onMounted(() => {
    // Якщо groupId переданий як getter (функція) — чекаємо доки значення з'явиться
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
