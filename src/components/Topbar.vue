<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/userStore'
import { request } from '@/api/request'

const props = defineProps<{
  currentBreadcrumb: { level1: string; level2: string }
}>()

const router = useRouter()
const userStore = useUserStore()
const showUserMenu = ref(false)

const currentUser = computed(() => userStore.currentUser)

const userInitials = computed(() => {
  const user = userStore.currentUser
  if (!user?.name) return 'U'
  return user.name.substring(0, 2).toUpperCase()
})

const userDisplayName = computed(() => {
  return userStore.currentUser?.name || '未登录'
})

const handleChangePassword = () => {
  showUserMenu.value = false
  router.push('/change-password')
}

const handleLogout = async () => {
  showUserMenu.value = false
  try {
    await request.post('/auth/logout')
  } catch (_e) {
    // 登出请求失败不影响本地清理
  }
  userStore.clearUser()
  router.push('/login')
}

const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.topbar__user')) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <header class="topbar">
    <div class="topbar__breadcrumb">
      <span class="topbar__breadcrumb-l1">{{ currentBreadcrumb.level1 }}</span>
      <span
        v-if="currentBreadcrumb.level2"
        class="topbar__breadcrumb-sep"
      >/</span>
      <span
        v-if="currentBreadcrumb.level2"
        class="topbar__breadcrumb-l2"
      >{{ currentBreadcrumb.level2 }}</span>
    </div>
    <div
      class="topbar__user"
      @click="showUserMenu = !showUserMenu"
    >
      <div class="topbar__avatar">
        {{ userInitials }}
      </div>
      <span class="topbar__username">{{ userDisplayName }}</span>
      <svg
        class="topbar__chevron"
        width="10"
        height="10"
        viewBox="0 0 10 10"
      >
        <path
          d="M2.5 3.75L5 6.25L7.5 3.75"
          stroke="currentColor"
          stroke-width="1.2"
          fill="none"
        />
      </svg>
      <Transition name="dropdown">
        <div
          v-if="showUserMenu"
          class="user-menu"
        >
          <div class="user-menu__role">
            {{ currentUser?.role || '未知角色' }}
          </div>
          <div class="user-menu__divider" />
          <div
            class="user-menu__item"
            @click.stop="handleChangePassword"
          >
            修改密码
          </div>
          <div
            class="user-menu__item user-menu__item--danger"
            @click.stop="handleLogout"
          >
            退出登录
          </div>
        </div>
      </Transition>
    </div>
  </header>
</template>

<style scoped>
.topbar {
  height: var(--topbar-height);
  background: var(--color-bg-card);
  border-bottom: 1px solid var(--color-border-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-6);
  flex-shrink: 0;
}

.topbar__breadcrumb {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
}

.topbar__breadcrumb-l1 {
  color: var(--color-text-secondary);
}

.topbar__breadcrumb-sep {
  color: var(--color-border);
}

.topbar__breadcrumb-l2 {
  color: var(--color-text-primary);
  font-weight: var(--weight-medium);
}

.topbar__user {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-md);
  transition: background var(--transition-fast);
  position: relative;
}

.topbar__user:hover {
  background: var(--color-bg-page);
}

.topbar__avatar {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  background: var(--color-primary);
  color: var(--color-bg-card);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: var(--weight-semibold);
  font-family: var(--font-mono);
  letter-spacing: 0.02em;
}

.topbar__username {
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  font-weight: var(--weight-medium);
}

.topbar__chevron {
  color: var(--color-text-secondary);
  transition: transform var(--transition-fast);
}

.user-menu {
  position: absolute;
  top: calc(100% + 4px);
  right: 0;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  min-width: 160px;
  overflow: hidden;
  z-index: var(--z-dropdown);
}

.user-menu__role {
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  font-family: var(--font-mono);
  letter-spacing: 0.04em;
}

.user-menu__divider {
  height: 1px;
  background: var(--color-border-light);
}

.user-menu__item {
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  color: var(--color-text-regular);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.user-menu__item:hover {
  background: var(--color-bg-page);
}

.user-menu__item--danger {
  color: var(--color-danger);
}

.user-menu__item--danger:hover {
  background: var(--color-danger-subtle);
}

.dropdown-enter-active {
  animation: slideDown var(--transition-fast) ease-out;
}

.dropdown-leave-active {
  animation: slideDown var(--transition-fast) ease-out reverse;
}
</style>
