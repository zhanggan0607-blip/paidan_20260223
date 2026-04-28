<template>
  <div
    class="layout"
    :class="{ 'layout--fullscreen': isFullscreenMode }"
  >
    <aside
      v-show="!isFullscreenMode"
      class="sidebar"
    >
      <div class="sidebar__header">
        <div class="sidebar__logo">
          <svg
            class="sidebar__logo-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
          >
            <path d="M12 2L2 7l10 5 10-5-10-5z" />
            <path d="M2 17l10 5 10-5" />
            <path d="M2 12l10 5 10-5" />
          </svg>
        </div>
        <h1 class="sidebar__title">
          SSTCP
        </h1>
        <span class="sidebar__subtitle">维保管理</span>
      </div>
      <nav class="sidebar__nav">
        <div
          v-for="menu in filteredMenuItems"
          :key="menu.id"
          class="nav-group"
        >
          <div
            class="nav-group__title"
            :class="{ 'nav-group__title--expandable': menu.children }"
            @click="toggleMenu(menu.id)"
          >
            <span class="nav-group__label">{{ menu.label }}</span>
            <span
              v-if="menu.children"
              class="nav-group__arrow"
              :class="{ 'nav-group__arrow--open': expandedMenus.includes(menu.id) }"
            >
              <svg
                width="12"
                height="12"
                viewBox="0 0 12 12"
              >
                <path
                  d="M4.5 2.5L8 6L4.5 9.5"
                  stroke="currentColor"
                  stroke-width="1.5"
                  fill="none"
                />
              </svg>
            </span>
          </div>
          <Transition name="submenu">
            <div
              v-if="menu.children && expandedMenus.includes(menu.id)"
              class="nav-group__submenu"
            >
              <div
                v-for="submenu in menu.children"
                :key="submenu.id"
                class="nav-item"
                :class="{ 'nav-item--active': activeMenu === submenu.id }"
                @click="handleMenuClick(submenu)"
              >
                <span class="nav-item__dot" />
                <span class="nav-item__text">{{ submenu.label }}</span>
              </div>
            </div>
          </Transition>
          <div
            v-if="!menu.children"
            class="nav-item"
            :class="{ 'nav-item--active': activeMenu === menu.id }"
            @click="handleMenuClick(menu)"
          >
            <span class="nav-item__dot" />
            <span class="nav-item__text">{{ menu.label }}</span>
          </div>
        </div>
      </nav>
      <div class="sidebar__footer">
        <div class="sidebar__version">V{{ appVersion }}</div>
      </div>
    </aside>

    <section class="main">
      <div class="main__inner">
        <header
          v-show="!isFullscreenMode"
          class="topbar"
        >
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
        <div class="content">
          <router-view />
        </div>
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, provide, readonly, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { MenuItem } from '@/types'
import { userStore } from '@/stores/userStore'
import { request } from '@/api/request'
import { version as appVersion } from '../../package.json'

const HEARTBEAT_INTERVAL = 2 * 60 * 1000

export default defineComponent({
  name: 'Layout',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const expandedMenus = ref<string[]>(['statistics'])
    const activeMenu = ref<string>('project-info')
    const isFullscreenMode = ref(false)
    const showUserMenu = ref(false)
    let heartbeatTimer: number | null = null

    const setFullscreenMode = (value: boolean) => {
      isFullscreenMode.value = value
    }

    provide('fullscreenMode', readonly(isFullscreenMode))
    provide('setFullscreenMode', setFullscreenMode)

    const currentUser = computed(() => userStore.getUser())

    const userInitials = computed(() => {
      const user = userStore.getUser()
      if (!user?.name) return 'U'
      return user.name.substring(0, 2).toUpperCase()
    })

    const userDisplayName = computed(() => {
      return userStore.getUser()?.name || '未登录'
    })

    const canShowMenu = (menuId: string): boolean => {
      if (!userStore.getUser()) return false
      return userStore.canShowMenu(menuId)
    }

    const sendHeartbeat = async () => {
      try {
        await request.post('/online/heartbeat', { device_type: 'pc' })
      } catch {
        // ignore
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

    const menuItems: MenuItem[] = [
      {
        id: 'statistics',
        label: '统计分析',
        path: '/statistics',
      },
      {
        id: 'maintenance',
        label: '维保项目管理',
        children: [
          { id: 'project-info', label: '项目信息管理', path: '/project-info' },
          { id: 'maintenance-plan', label: '维保计划管理', path: '/maintenance-plan' },
          { id: 'overdue-alert', label: '项目超期提醒', path: '/overdue-alert' },
          { id: 'near-expiry-alert', label: '项目临期提醒', path: '/near-expiry-alert' },
        ],
      },
      {
        id: 'work-order',
        label: '工单管理',
        children: [
          { id: 'work-plan', label: '定期巡检单查询', path: '/work-plan' },
          { id: 'temporary-repair', label: '临时维修单查询', path: '/work-order/temporary-repair' },
          { id: 'spot-work', label: '零星用工单查询', path: '/work-order/spot-work' },
        ],
      },
      {
        id: 'spare-parts',
        label: '备品备件管理',
        children: [
          { id: 'spare-parts-issue', label: '备品备件领用', path: '/spare-parts/issue' },
          { id: 'spare-parts-return', label: '备品备件归还', path: '/spare-parts/return' },
          { id: 'spare-parts-stock', label: '备品备件库存', path: '/spare-parts/stock' },
        ],
      },
      {
        id: 'repair-tools',
        label: '维修工具管理',
        children: [
          { id: 'repair-tools-issue', label: '维修工具领用', path: '/repair-tools/issue' },
          { id: 'repair-tools-return', label: '维修工具归还', path: '/repair-tools/return' },
          { id: 'repair-tools-inbound', label: '维修工具库存', path: '/repair-tools/inbound' },
        ],
      },
      {
        id: 'maintenance-log',
        label: '维保日志',
        children: [
          { id: 'maintenance-log-fill', label: '新报维保日志', path: '/maintenance-log/fill' },
          { id: 'maintenance-log-list', label: '维保日志查询', path: '/maintenance-log/list' },
          { id: 'weekly-report-fill', label: '新报部门周报', path: '/weekly-report/fill' },
          { id: 'weekly-report-list', label: '部门周报查询', path: '/weekly-report/list' },
        ],
      },
      {
        id: 'system',
        label: '系统管理',
        children: [
          { id: 'personnel', label: '人员管理', path: '/personnel' },
          { id: 'customer', label: '客户管理', path: '/customer' },
          { id: 'inspection-item', label: '巡检事项管理', path: '/inspection-item' },
        ],
      },
    ]

    const filteredMenuItems = computed(() => {
      return menuItems
        .filter((menu) => {
          if (menu.children) {
            const filteredChildren = menu.children.filter((child) => canShowMenu(child.id))
            return filteredChildren.length > 0
          }
          return canShowMenu(menu.id)
        })
        .map((menu) => {
          if (menu.children) {
            return {
              ...menu,
              children: menu.children.filter((child) => canShowMenu(child.id)),
            }
          }
          return menu
        })
    })

    const currentBreadcrumb = computed(() => {
      const path = route.path
      if (path === '/statistics') {
        return { level1: '统计分析', level2: '数据看板' }
      }
      for (const menu of menuItems) {
        if (menu.children) {
          const child = menu.children.find((c) => c.path === path)
          if (child) {
            return { level1: menu.label, level2: child.label }
          }
        }
      }
      return { level1: '维保项目管理', level2: '项目信息管理' }
    })

    const toggleMenu = (menuId: string) => {
      if (expandedMenus.value.includes(menuId)) {
        expandedMenus.value = expandedMenus.value.filter((id) => id !== menuId)
      } else {
        expandedMenus.value = [...expandedMenus.value, menuId]
      }
    }

    const handleMenuClick = (item: MenuItem) => {
      activeMenu.value = item.id
      const parentMenu = menuItems.find(
        (menu) => menu.children && menu.children.some((child) => child.id === item.id)
      )
      if (parentMenu && parentMenu.id) {
        if (!expandedMenus.value.includes(parentMenu.id)) {
          expandedMenus.value = [...expandedMenus.value, parentMenu.id]
        }
      }
      if (item.path) {
        router.push({ path: item.path })
      }
    }

    const handleChangePassword = () => {
      showUserMenu.value = false
      router.push('/change-password')
    }

    const handleLogout = async () => {
      showUserMenu.value = false
      try {
        await request.post('/auth/logout')
      } catch {
        // ignore
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
      startHeartbeat()
    })

    onUnmounted(() => {
      document.removeEventListener('click', handleClickOutside)
      stopHeartbeat()
    })

    return {
      appVersion,
      filteredMenuItems,
      expandedMenus,
      activeMenu,
      currentBreadcrumb,
      toggleMenu,
      handleMenuClick,
      isFullscreenMode,
      currentUser,
      userInitials,
      userDisplayName,
      showUserMenu,
      handleChangePassword,
      handleLogout,
    }
  },
})
</script>

<style scoped>
.layout {
  display: grid;
  grid-template-columns: var(--sidebar-width) 1fr;
  min-height: 100vh;
  background: var(--color-bg-page);
}

.layout--fullscreen {
  grid-template-columns: 1fr;
}

.sidebar {
  background: var(--color-sidebar-bg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.sidebar::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 1px;
  background: var(--color-sidebar-border);
}

.sidebar__header {
  padding: var(--space-5) var(--space-4);
  display: flex;
  align-items: center;
  gap: var(--space-2);
  border-bottom: 1px solid var(--color-sidebar-border);
}

.sidebar__logo {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary-light);
  flex-shrink: 0;
}

.sidebar__logo-icon {
  width: 24px;
  height: 24px;
}

.sidebar__title {
  font-family: var(--font-mono);
  font-size: var(--text-lg);
  font-weight: var(--weight-bold);
  color: var(--color-sidebar-text-active);
  letter-spacing: 0.08em;
  line-height: 1;
}

.sidebar__subtitle {
  font-size: var(--text-xs);
  color: var(--color-sidebar-text);
  opacity: 0.6;
  margin-left: auto;
  letter-spacing: 0.04em;
}

.sidebar__nav {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-2) 0;
}

.nav-group {
  margin-bottom: 1px;
}

.nav-group__title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-2) var(--space-4);
  cursor: pointer;
  transition: background var(--transition-fast);
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  color: var(--color-sidebar-text);
  letter-spacing: 0.02em;
  user-select: none;
}

.nav-group__title:hover {
  background: var(--color-sidebar-hover);
}

.nav-group__title--expandable {
  cursor: pointer;
}

.nav-group__arrow {
  display: flex;
  align-items: center;
  color: var(--color-sidebar-text);
  opacity: 0.4;
  transition: transform var(--transition-normal), opacity var(--transition-fast);
}

.nav-group__arrow--open {
  transform: rotate(90deg);
  opacity: 0.7;
}

.nav-group__submenu {
  overflow: hidden;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-1) var(--space-4) var(--space-1) var(--space-6);
  cursor: pointer;
  transition: background var(--transition-fast), color var(--transition-fast);
  font-size: var(--text-sm);
  color: var(--color-sidebar-text);
  opacity: 0.75;
  user-select: none;
}

.nav-item:hover {
  background: var(--color-sidebar-hover);
  opacity: 1;
}

.nav-item--active {
  background: var(--color-sidebar-active);
  color: var(--color-sidebar-text-active);
  opacity: 1;
}

.nav-item__dot {
  width: 4px;
  height: 4px;
  border-radius: var(--radius-full);
  background: currentColor;
  opacity: 0.4;
  flex-shrink: 0;
}

.nav-item--active .nav-item__dot {
  opacity: 1;
  background: var(--color-primary-light);
}

.nav-item__text {
  line-height: var(--leading-tight);
}

.sidebar__footer {
  padding: var(--space-3) var(--space-4);
}

.sidebar__version {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--color-sidebar-text);
  opacity: 0.35;
  letter-spacing: 0.06em;
}

.main {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--color-bg-page);
}

.main__inner {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

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

.content {
  flex: 1;
  overflow: auto;
  padding: var(--space-5);
}

.submenu-enter-active,
.submenu-leave-active {
  transition: all var(--transition-normal);
  overflow: hidden;
}

.submenu-enter-from,
.submenu-leave-to {
  opacity: 0;
  max-height: 0;
}

.submenu-enter-to,
.submenu-leave-from {
  opacity: 1;
  max-height: 500px;
}

.dropdown-enter-active {
  animation: slideDown var(--transition-fast) ease-out;
}

.dropdown-leave-active {
  animation: slideDown var(--transition-fast) ease-out reverse;
}
</style>
