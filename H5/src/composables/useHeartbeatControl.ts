import { ref } from 'vue'

const isPaused = ref(false)
let pauseCount = 0

export const useHeartbeatControl = {
  pause() {
    pauseCount++
    isPaused.value = true
  },

  resume() {
    pauseCount = Math.max(0, pauseCount - 1)
    if (pauseCount === 0) {
      isPaused.value = false
    }
  },

  isPaused() {
    return isPaused.value
  },
}

export default useHeartbeatControl
