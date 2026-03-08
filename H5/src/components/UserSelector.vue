<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { showSuccessToast, showLoadingToast, closeToast, showToast } from 'vant'
import { authService, personnelService, onlineUserService } from '../services'
import { userStore, type User } from '../stores/userStore'

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
 * @returns 登录结果: 'success' | 'password_changed' | 'error'
 */
const loginUser = async (user: User): Promise<'success' | 'password_changed' | 'error'> => {
  try {
    showLoadingToast({
      message: '登录中...',
      forbidClick: true,
      duration: 0,
    })

    const defaultPassword = user.phone ? user.phone.slice(-6) : '123456'

    const response = await authService.login({
      username: user.name,
      password: defaultPassword,
      device_type: 'h5',
    })

    closeToast()

    if (response.code === 200 && response.data?.access_token) {
      userStore.setToken(response.data.access_token)
      onlineUserService.recordLogin('h5', user.id, user.name).catch(() => {})
      return 'success'
    }

    return 'error'
  } catch (error: any) {
    closeToast()
    console.error('登录失败:', error)
    if (error?.status === 401) {
      return 'password_changed'
    }
    return 'error'
  }
}

const loadUserList = async () => {
  try {
    const response = await personnelService.getAll()
    if (response.code === 200 && response.data) {
      const data = Array.isArray(response.data) ? response.data : []
      userList.value = data.map((p) => ({
        id: p.id,
        name: p.name,
        role: p.role || '',
        department: p.department || '',
        phone: p.phone || '',
      }))
      const savedUser = userStore.getUser()
      if (savedUser) {
        const loginResult = await loginUser(savedUser)
        if (loginResult !== 'success') {
          console.warn('保存的用户登录失败，清除并尝试其他用户')
          userStore.clearUser()
          for (const user of userList.value) {
            const retryResult = await loginUser(user)
            if (retryResult === 'success') {
              userStore.setUser(user)
              break
            }
          }
        }
      } else if (userList.value.length > 0) {
        for (const user of userList.value) {
          const loginResult = await loginUser(user)
          if (loginResult === 'success') {
            userStore.setUser(user)
            break
          }
        }
      }
      isReady.value = true
      if (userStore.isLoggedIn() && currentUser.value) {
        emit('ready', currentUser.value)
      } else {
        console.error('所有用户登录失败，无法继续')
      }
    }
  } catch (error) {
    console.error('加载用户列表失败:', error)
    isReady.value = true
    if (userStore.isLoggedIn() && currentUser.value) {
      emit('ready', currentUser.value)
    }
  }
}

const selectUser = async (user: User) => {
  const loginResult = await loginUser(user)
  if (loginResult === 'success') {
    userStore.setUser(user)
    showPopover.value = false
    showSuccessToast(`已切换到用户: ${user.name}`)
    emit('userChanged', user)
  } else if (loginResult === 'password_changed') {
    showToast({
      message: `${user.name} 已修改密码，无法自动登录`,
      position: 'top',
    })
  } else {
    showToast({
      message: '登录失败，请重试',
      position: 'top',
    })
  }
}

const userOptions = computed(() => {
  return userList.value.map((user) => ({
    text: `${user.name} (${user.role})`,
    disabled: currentUser.value?.id === user.id,
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
  isReady,
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
      <div v-if="currentUser" class="user-selector">
        <span class="user-name">{{ currentUser.name }}</span>
        <span v-if="currentUser.role" class="user-role">({{ currentUser.role }})</span>
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
