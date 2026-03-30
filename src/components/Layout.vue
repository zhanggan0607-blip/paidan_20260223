<template>
  <div class="layout" :class="{ 'fullscreen-mode': isFullscreenMode }">
    <aside v-show="!isFullscreenMode" class="sidebar">
      <div class="sidebar-header">
        <h1 class="system-title">SSTCP维保系统</h1>
      </div>
      <nav class="sidebar-nav">
        <div v-for="menu in filteredMenuItems" :key="menu.id" class="menu-group">
          <div class="menu-title" @click="toggleMenu(menu.id)">
            <span class="menu-label">{{ menu.label }}</span>
            <span
              v-if="menu.children"
              class="menu-arrow"
              :class="{ expanded: expandedMenus.includes(menu.id) }"
            >
              ▶
            </span>
          </div>
          <div v-if="menu.children && expandedMenus.includes(menu.id)" class="submenu">
            <div
              v-for="submenu in menu.children"
              :key="submenu.id"
              class="submenu-item"
              :class="{ active: activeMenu === submenu.id }"
              @click="handleMenuClick(submenu)"
            >
              {{ submenu.label }}
            </div>
          </div>
          <div
            v-if="!menu.children"
            class="submenu-item"
            :class="{ active: activeMenu === menu.id }"
            @click="handleMenuClick(menu)"
          >
            {{ menu.label }}
          </div>
        </div>
      </nav>
    </aside>

    <section class="center-content">
      <div class="main-content">
        <div v-show="!isFullscreenMode" class="top-bar">
          <div class="breadcrumb">
            <span class="breadcrumb-level1">{{ currentBreadcrumb.level1 }}</span>
            <span v-if="currentBreadcrumb.level2" class="breadcrumb-separator">/</span>
            <span class="breadcrumb-level2">{{ currentBreadcrumb.level2 }}</span>
          </div>
          <div class="user-info" @click="showUserMenu = !showUserMenu">
            <div class="user-avatar">{{ userInitials }}</div>
            <span class="user-name">{{ userDisplayName }}</span>
            <span class="dropdown-arrow">▼</span>
            <div v-if="showUserMenu" class="user-dropdown">
              <div class="dropdown-item user-role">
                {{ currentUser?.role || '未知角色' }}
              </div>
              <div class="dropdown-divider"></div>
              <div class="dropdown-item" @click.stop="handleChangePassword">修改密码</div>
              <div class="dropdown-item logout" @click.stop="handleLogout">退出登录</div>
            </div>
          </div>
        </div>
        <div class="content-wrapper">
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
import api from '@/utils/api'

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
        await api.post('/online/heartbeat', { device_type: 'pc' })
      } catch {
        // 忽略心跳错误
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
        await api.post('/auth/logout')
      } catch {
        // 忽略登出错误
      }
      userStore.clearUser()
      router.push('/login')
    }

    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement
      if (!target.closest('.user-info')) {
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
  grid-template-columns: 240px 1fr;
  min-height: 100vh;
}

.layout.fullscreen-mode {
  grid-template-columns: 1fr;
}

.layout.fullscreen-mode .center-content {
  width: 100%;
  max-width: 100%;
}

.sidebar {
  width: 240px;
  background: #001f3f;
  color: #fff;
  display: flex;
  flex-direction: column;
  box-shadow: 1px 0 4px rgba(0, 0, 0, 0.08);
}

.sidebar-header {
  padding: 20px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(0, 0, 0, 0.05);
}

.system-title {
  font-size: 22px;
  font-weight: 700;
  color: #fff;
  text-align: center;
  letter-spacing: 0.3px;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.menu-group {
  margin-bottom: 2px;
}

.menu-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  cursor: pointer;
  transition: background 0.15s;
  font-weight: 600;
  font-size: 16px;
}

.menu-title:hover {
  background: rgba(255, 255, 255, 0.08);
}

.menu-label {
  flex: 1;
}

.menu-arrow {
  font-size: 8px;
  transition: transform 0.15s;
  margin-left: 8px;
}

.menu-arrow.expanded {
  transform: rotate(90deg);
}

.submenu {
  background: rgba(0, 0, 0, 0.08);
}

.submenu-item {
  padding: 8px 16px 8px 36px;
  cursor: pointer;
  transition: background 0.15s;
  font-size: 16px;
  text-align: left;
}

.submenu-item:hover {
  background: rgba(255, 255, 255, 0.06);
}

.submenu-item.active {
  background: rgba(255, 255, 255, 0.12);
  border-left: 3px solid #90caf9;
}

.center-content {
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
  overflow: hidden;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.top-bar {
  height: 56px;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.breadcrumb {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #666;
}

.breadcrumb-level1 {
  color: #999;
}

.breadcrumb-separator {
  margin: 0 8px;
  color: #ccc;
}

.breadcrumb-level2 {
  color: #333;
  font-weight: 500;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 20px;
  transition: background 0.2s;
  position: relative;
}

.user-info:hover {
  background: #f5f5f5;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  margin-right: 8px;
}

.user-name {
  font-size: 14px;
  color: #333;
  margin-right: 4px;
}

.dropdown-arrow {
  font-size: 10px;
  color: #999;
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  min-width: 160px;
  z-index: 1000;
  overflow: hidden;
}

.dropdown-item {
  padding: 12px 16px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: background 0.15s;
}

.dropdown-item:hover {
  background: #f5f5f5;
}

.dropdown-item.user-role {
  color: #666;
  font-size: 12px;
  cursor: default;
}

.dropdown-item.user-role:hover {
  background: transparent;
}

.dropdown-item.logout {
  color: #e74c3c;
}

.dropdown-item.logout:hover {
  background: #fdf2f2;
}

.dropdown-divider {
  height: 1px;
  background: #eee;
  margin: 4px 0;
}

.content-wrapper {
  flex: 1;
  overflow: auto;
  padding: 20px;
}
</style>
