import { ref } from 'vue'

const dingtalkAuthReady = ref(false)
const isDingtalkEnv = ref(false)

export function useDingtalkAuth() {
  return { dingtalkAuthReady, isDingtalkEnv }
}
