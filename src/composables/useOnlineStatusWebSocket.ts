/**
 * WebSocket连接composable
 * 用于实时接收用户在线状态变化
 */
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useUserStore } from '../stores/userStore'

interface OnlineStatusData {
  user_id: number
  user_name: string
  is_online: boolean
  device_type: string | null
  timestamp: string
}

interface OnlineUser {
  user_id: number
  user_name: string
  device_type: string | null
  is_online: boolean
}

interface OnlineUsersListData {
  users: OnlineUser[]
  count: number
  timestamp?: string
}

interface WebSocketMessage {
  type: 'online_status' | 'online_users_list' | 'pong'
  data: OnlineStatusData | OnlineUsersListData | null
}

function getWebSocketUrl(token: string | null): string {
  const protocol =
    typeof window !== 'undefined' && window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = typeof window !== 'undefined' ? window.location.host : 'localhost:8000'
  const baseUrl = `${protocol}//${host}/api/v1/ws/online-status`
  if (token) {
    return `${baseUrl}?token=${encodeURIComponent(token)}`
  }
  return baseUrl
}

export function useOnlineStatusWebSocket() {
  const userStore = useUserStore()
  const ws = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  const onlineUsers = ref<Map<number, { is_online: boolean; device_type: string | null }>>(
    new Map()
  )
  const reconnectAttempts = ref(0)
  const maxReconnectAttempts = 5

  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  let pingTimer: ReturnType<typeof setInterval> | null = null

  const connect = () => {
    if (ws.value?.readyState === WebSocket.OPEN) {
      return
    }

    const token = userStore.getToken()
    if (!token) {
      return
    }

    try {
      const wsUrl = getWebSocketUrl(token)
      ws.value = new WebSocket(wsUrl)

      ws.value.onopen = () => {
        isConnected.value = true
        reconnectAttempts.value = 0
        startPing()
      }

      ws.value.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          handleMessage(message)
        } catch (e) {
          console.error('[WebSocket] 解析消息失败:', e)
        }
      }

      ws.value.onclose = (event) => {
        isConnected.value = false
        stopPing()
        if (event.code === 4001) {
          console.warn('[WebSocket] 认证失败，token可能已过期')
          return
        }
        attemptReconnect()
      }

      ws.value.onerror = (error) => {
        console.error('[WebSocket] 连接错误:', error)
        isConnected.value = false
      }
    } catch (error) {
      console.error('[WebSocket] 创建连接失败:', error)
      attemptReconnect()
    }
  }

  const disconnect = () => {
    stopPing()
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    if (ws.value) {
      ws.value.close()
      ws.value = null
    }
    isConnected.value = false
  }

  const attemptReconnect = () => {
    if (reconnectAttempts.value >= maxReconnectAttempts) {
      return
    }

    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.value), 30000)

    reconnectTimer = setTimeout(() => {
      reconnectAttempts.value++
      connect()
    }, delay)
  }

  const startPing = () => {
    pingTimer = setInterval(() => {
      if (ws.value?.readyState === WebSocket.OPEN) {
        ws.value.send('ping')
      }
    }, 30000)
  }

  const stopPing = () => {
    if (pingTimer) {
      clearInterval(pingTimer)
      pingTimer = null
    }
  }

  const handleMessage = (message: WebSocketMessage) => {
    switch (message.type) {
      case 'online_status':
        handleOnlineStatus(message.data as OnlineStatusData)
        break
      case 'online_users_list':
        handleOnlineUsersList(message.data as OnlineUsersListData)
        break
      case 'pong':
        break
    }
  }

  const handleOnlineStatus = (data: OnlineStatusData) => {
    onlineUsers.value.set(data.user_id, {
      is_online: data.is_online,
      device_type: data.device_type,
    })
  }

  const handleOnlineUsersList = (data: OnlineUsersListData) => {
    const newMap = new Map<number, { is_online: boolean; device_type: string | null }>()
    for (const user of data.users) {
      newMap.set(user.user_id, {
        is_online: user.is_online,
        device_type: user.device_type,
      })
    }
    onlineUsers.value = newMap
  }

  const refreshOnlineUsers = () => {
    if (ws.value?.readyState === WebSocket.OPEN) {
      ws.value.send('refresh')
    }
  }

  const getUserOnlineStatus = (userId: number) => {
    return onlineUsers.value.get(userId) || { is_online: false, device_type: null }
  }

  watch(() => userStore.token, (newToken, oldToken) => {
    if (newToken && newToken !== oldToken) {
      disconnect()
      reconnectAttempts.value = 0
      connect()
    } else if (!newToken) {
      disconnect()
      onlineUsers.value = new Map()
    }
  })

  onMounted(() => {
    connect()
  })

  onUnmounted(() => {
    disconnect()
  })

  return {
    isConnected,
    onlineUsers,
    connect,
    disconnect,
    refreshOnlineUsers,
    getUserOnlineStatus,
  }
}
