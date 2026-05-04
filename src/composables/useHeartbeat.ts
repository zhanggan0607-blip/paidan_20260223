import { onMounted, onUnmounted } from 'vue'
import { request } from '@/api/request'

const HEARTBEAT_INTERVAL = 2 * 60 * 1000
let heartbeatTimer: number | null = null

const sendHeartbeat = async () => {
  try {
    await request.post('/online/heartbeat', { device_type: 'pc' })
  } catch (_e) {
    // 心跳失败不影响用户体验
  }
}

const startHeartbeat = () => {
  stopHeartbeat()
  sendHeartbeat()
  heartbeatTimer = window.setInterval(sendHeartbeat, HEARTBEAT_INTERVAL)
}

const stopHeartbeat = () => {
  if (heartbeatTimer) {
    clearInterval(heartbeatTimer)
    heartbeatTimer = null
  }
}

export function useHeartbeat() {
  onMounted(() => {
    startHeartbeat()
  })

  onUnmounted(() => {
    stopHeartbeat()
  })

  return { startHeartbeat, stopHeartbeat }
}
