<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { showSuccessToast } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import { authService, type User } from '../services/auth'

const emit = defineEmits<{
  (e: 'userChanged'): void
  (e: 'ready'): void
}>()

const currentUser = ref<User | null>(null)
const userList = ref<User[]>([])
const showPopover = ref(false)
const isReady = ref(false)

const loadUserList = async () => {
  try {
    const response = await api.get<unknown, ApiResponse<{content: User[]}>>('/personnel')
    if (response.code === 200 && response.data) {
      userList.value = response.data.content || []
      const savedUser = authService.getCurrentUser()
      if (savedUser) {
        currentUser.value = savedUser
      } else if (userList.value.length > 0) {
        currentUser.value = userList.value[0]
        authService.updateStoredUser(userList.value[0])
      }
      isReady.value = true
      emit('ready')
    }
  } catch (error) {
    console.error('加载用户列表失败:', error)
    isReady.value = true
    emit('ready')
  }
}

const selectUser = (user: User) => {
  currentUser.value = user
  authService.updateStoredUser(user)
  showPopover.value = false
  showSuccessToast(`已切换到用户: ${user.name}`)
  emit('userChanged')
}

const userOptions = computed(() => {
  return userList.value.map(user => ({
    text: `${user.name} (${user.role})`,
    disabled: currentUser.value?.id === user.id
  }))
})

const onSelectUser = (action: { text: string }, index: number) => {
  const user = userList.value[index]
  if (user && currentUser.value?.id !== user.id) {
    selectUser(user)
  }
}

onMounted(() => {
  loadUserList()
})

defineExpose({
  currentUser,
  isReady
})
</script>

<template>
  <van-popover
    v-model:show="showPopover"
    :actions="userOptions"
    placement="bottom-end"
    trigger="click"
    theme="light"
    @select="onSelectUser"
  >
    <template #reference>
      <div class="user-selector" v-if="currentUser">
        <span class="user-name">{{ currentUser.name }}</span>
        <span class="user-role" v-if="currentUser.role">({{ currentUser.role }})</span>
        <van-icon name="arrow-down" />
      </div>
    </template>
  </van-popover>
</template>

<style scoped>
.user-selector {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  position: relative;
  padding: 8px;
  -webkit-tap-highlight-color: transparent;
}

.user-name {
  font-size: 14px;
  color: #323233;
}

.user-role {
  font-size: 12px;
  color: #969799;
}
</style>
