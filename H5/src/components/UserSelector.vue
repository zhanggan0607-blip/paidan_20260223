<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { showSuccessToast, showLoadingToast, closeToast } from 'vant'
import { authService } from '../services/auth'
import { personnelService } from '../services/personnel'
import { userStore, type User } from '../stores/userStore'
import { onlineUserService } from '../services/onlineUser'

const emit = defineEmits<{
  (e: 'userChanged', user: User): void
  (e: 'ready', user: User): void
}>()

const userList = ref<User[]>([])
const showPopover = ref(false)
const isReady = ref(false)

const currentUser = computed(() => userStore.readonlyCurrentUser.value)

/**
 * 用户登录获取token
 * @param user 用户信息
 */
const loginUser = async (user: User): Promise<boolean> => {
  try {
    showLoadingToast({
      message: '登录中...',
      forbidClick: true,
      duration: 0
    })
    
    const defaultPassword = user.phone ? user.phone.slice(-6) : '123456'
    
    const response = await authService.login({
      username: user.name,
      password: defaultPassword,
      device_type: 'h5'
    })
    
    closeToast()
    
    if (response.code === 200 && response.data?.access_token) {
      userStore.setToken(response.data.access_token)
      onlineUserService.recordLogin('h5', user.id, user.name).catch(() => {})
      return true
    }
    
    return false
  } catch (error) {
    closeToast()
    console.error('登录失败:', error)
    return false
  }
}

const loadUserList = async () => {
  try {
    const response = await personnelService.getAll()
    if (response.code === 200 && response.data) {
      const data = Array.isArray(response.data) ? response.data : []
      userList.value = data.map(p => ({
        id: p.id,
        name: p.name,
        role: p.role || '',
        department: p.department || '',
        phone: p.phone || ''
      }))
      const savedUser = userStore.getUser()
      if (savedUser) {
        const loginSuccess = await loginUser(savedUser)
        if (!loginSuccess) {
          console.error('自动登录失败')
        }
      } else if (userList.value.length > 0) {
        const firstUser = userList.value[0]
        if (firstUser) {
          const loginSuccess = await loginUser(firstUser)
          if (loginSuccess) {
            userStore.setUser(firstUser)
          }
        }
      }
      isReady.value = true
      if (currentUser.value) {
        emit('ready', currentUser.value)
      }
    }
  } catch (error) {
    console.error('加载用户列表失败:', error)
    isReady.value = true
    if (currentUser.value) {
      emit('ready', currentUser.value)
    }
  }
}

const selectUser = async (user: User) => {
  const loginSuccess = await loginUser(user)
  if (loginSuccess) {
    userStore.setUser(user)
    showPopover.value = false
    showSuccessToast(`已切换到用户: ${user.name}`)
    emit('userChanged', user)
  } else {
    showSuccessToast('登录失败，请重试')
  }
}

const userOptions = computed(() => {
  return userList.value.map(user => ({
    text: `${user.name} (${user.role})`,
    disabled: currentUser.value?.id === user.id
  }))
})

const onSelectUser = (_action: { text: string }, index: number) => {
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
