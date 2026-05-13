import { ref } from 'vue'

const isPaused = ref(false)
let pauseCount = 0

export function useHeartbeatControl() {
  const pause = () => {
    pauseCount++
    isPaused.value = true
  }

  const resume = () => {
    pauseCount = Math.max(0, pauseCount - 1)
    if (pauseCount === 0) {
      isPaused.value = false
    }
  }

  const getIsPaused = () => {
    return isPaused.value
  }

  return {
    isPaused,
    pause,
    resume,
    getIsPaused,
  }
}

export default useHeartbeatControl
