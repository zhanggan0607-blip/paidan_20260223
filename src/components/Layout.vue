<template>
  <!-- TODO: Layout组件 - 考虑加入主题切换功能 -->
  <!-- FIXME: 全屏模式下ESC键退出功能在某些浏览器不生效 -->
  <div class="layout" :class="{ 'fullscreen-mode': isFullscreenMode }">
    <aside class="sidebar" v-show="!isFullscreenMode">
        <div class="sidebar-header">
          <h1 class="system-title">SSTCP维保系统</h1>
        </div>
       <nav class="sidebar-nav">
         <div
           v-for="menu in filteredMenuItems"
           :key="menu.id"
           class="menu-group"
         >
           <div
             class="menu-title"
             @click="toggleMenu(menu.id)"
           >
             <span class="menu-label">{{ menu.label }}</span>
             <span
               v-if="menu.children"
               class="menu-arrow"
               :class="{ expanded: expandedMenus.includes(menu.id) }"
             >
               ▶
             </span>
           </div>
           <div
             v-if="menu.children && expandedMenus.includes(menu.id)"
             class="submenu"
           >
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
        <div class="top-bar" v-show="!isFullscreenMode">
        <div class="breadcrumb">
          <span class="breadcrumb-level1">{{ currentBreadcrumb.level1 }}</span>
          <span class="breadcrumb-separator" v-if="currentBreadcrumb.level2">/</span>
          <span class="breadcrumb-level2">{{ currentBreadcrumb.level2 }}</span>
        </div>
        <div class="user-info" @click="showUserMenu = !showUserMenu">
          <div class="user-avatar">{{ userInitials }}</div>
          <span class="user-name">{{ userDisplayName }}</span>
          <span class="dropdown-arrow">▼</span>
          <div v-if="showUserMenu" class="user-dropdown">
            <div 
              v-for="user in userList" 
              :key="user.id" 
              class="dropdown-item" 
              :class="{ 'active': currentUser?.id === user.id }"
              @click.stop="selectUser(user)"
            >
              {{ user.name }} ({{ user.role }})
            </div>
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
import { defineComponent, ref, computed, provide, readonly, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { MenuItem } from '@/types'
import { userStore, type User } from '@/stores/userStore'
import { personnelService } from '@/services/personnel'
import { USER_ROLES } from '@/config/constants'
import { canShowMenu as checkMenuPermission } from '@/config/permission'

export default defineComponent({
  name: 'Layout',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const expandedMenus = ref<string[]>(['statistics'])
    const activeMenu = ref<string>('project-info')
    const isFullscreenMode = ref(false)

    const setFullscreenMode = (value: boolean) => {
      isFullscreenMode.value = value
    }

    provide('fullscreenMode', readonly(isFullscreenMode))
    provide('setFullscreenMode', setFullscreenMode)

    const userInitials = computed(() => {
      const user = userStore.getUser()
      if (!user?.name) return 'U'
      return user.name.substring(0, 2).toUpperCase()
    })

    const userDisplayName = computed(() => {
      return userStore.getUser()?.name || '未登录'
    })

    const userRoleDisplay = computed(() => {
      return userStore.getUser()?.role || ''
    })

    const getRoleClass = (role: string) => {
      switch (role) {
        case USER_ROLES.ADMIN:
          return 'role-admin'
        case USER_ROLES.DEPARTMENT_MANAGER:
          return 'role-manager'
        case USER_ROLES.MATERIAL_MANAGER:
          return 'role-material'
        case USER_ROLES.EMPLOYEE:
          return 'role-employee'
        default:
          return ''
      }
    }

    const handleLogout = () => {
      userStore.clearUser()
    }

    const canShowMenu = (menuId: string): boolean => {
      if (!userStore.getUser()) return false
      return userStore.canShowMenu(menuId)
    }

    const menuItems: MenuItem[] = [
      {
        id: 'statistics',
        label: '统计分析',
        path: '/statistics'
      },
      {
        id: 'maintenance',
        label: '维保项目管理',
        children: [
          { id: 'project-info', label: '项目信息管理', path: '/project-info' },
          { id: 'maintenance-plan', label: '维保计划管理', path: '/maintenance-plan' },
          { id: 'overdue-alert', label: '项目超期提醒', path: '/overdue-alert' },
          { id: 'near-expiry-alert', label: '项目临期提醒', path: '/near-expiry-alert' }
        ]
      },
      {
        id: 'work-order',
        label: '工单管理',
        children: [
          { id: 'work-plan', label: '定期巡检单查询', path: '/work-plan' },
          { id: 'temporary-repair', label: '临时维修单查询', path: '/work-order/temporary-repair' },
          { id: 'spot-work', label: '零星用工单查询', path: '/work-order/spot-work' }
        ]
      },
      {
        id: 'spare-parts',
        label: '备品备件管理',
        children: [
          { id: 'spare-parts-issue', label: '备品备件领用', path: '/spare-parts/issue' },
          { id: 'spare-parts-return', label: '备品备件归还', path: '/spare-parts/return' },
          { id: 'spare-parts-stock', label: '备品备件库存', path: '/spare-parts/stock' }
        ]
      },
      {
        id: 'repair-tools',
        label: '维修工具管理',
        children: [
          { id: 'repair-tools-issue', label: '维修工具领用', path: '/repair-tools/issue' },
          { id: 'repair-tools-return', label: '维修工具归还', path: '/repair-tools/return' },
          { id: 'repair-tools-inbound', label: '维修工具库存', path: '/repair-tools/inbound' }
        ]
      },
      {
        id: 'maintenance-log',
        label: '维保日志',
        children: [
          { id: 'maintenance-log-fill', label: '新报维保日志', path: '/maintenance-log/fill' },
          { id: 'maintenance-log-list', label: '维保日志查询', path: '/maintenance-log/list' },
          { id: 'weekly-report-fill', label: '新报部门周报', path: '/weekly-report/fill' },
          { id: 'weekly-report-list', label: '部门周报查询', path: '/weekly-report/list' }
        ]
      },
      {
        id: 'system',
        label: '系统管理',
        children: [
          { id: 'personnel', label: '人员管理', path: '/personnel' },
          { id: 'customer', label: '客户管理', path: '/customer' },
          { id: 'inspection-item', label: '巡检事项管理', path: '/inspection-item' }
        ]
      }
    ]

    const filteredMenuItems = computed(() => {
      return menuItems.filter(menu => {
        if (menu.children) {
          const filteredChildren = menu.children.filter(child => canShowMenu(child.id))
          return filteredChildren.length > 0
        }
        return canShowMenu(menu.id)
      }).map(menu => {
        if (menu.children) {
          return {
            ...menu,
            children: menu.children.filter(child => canShowMenu(child.id))
          }
        }
        return menu
      })
    })

    const currentBreadcrumb = computed(() => {
      const path = route.path
      if (path === '/statistics') {
        return {
          level1: '统计分析',
          level2: '数据看板',
          full: '统计分析 / 数据看板'
        }
      }
      for (const menu of menuItems) {
        if (menu.children) {
          const child = menu.children.find(c => c.path === path)
          if (child) {
            return {
              level1: menu.label,
              level2: child.label,
              full: `${menu.label} / ${child.label}`
            }
          }
        }
      }
      if (path === '/work-order/temporary-repair') {
        return {
          level1: '工单管理',
          level2: '临时维修单查询',
          full: '工单管理 / 临时维修单查询'
        }
      }
      if (path === '/work-order/spot-work') {
        return {
          level1: '工单管理',
          level2: '零星用工单查询',
          full: '工单管理 / 零星用工单查询'
        }
      }
      if (path === '/work-plan') {
        return {
          level1: '工单管理',
          level2: '定期巡检单查询',
          full: '工单管理 / 定期巡检单查询'
        }
      }
      if (path === '/spare-parts/issue') {
        return {
          level1: '备品备件管理',
          level2: '备品备件领用',
          full: '备品备件管理 / 备品备件领用'
        }
      }
      if (path === '/spare-parts/return') {
        return {
          level1: '备品备件管理',
          level2: '备品备件归还',
          full: '备品备件管理 / 备品备件归还'
        }
      }
      if (path === '/spare-parts/stock') {
        return {
          level1: '备品备件管理',
          level2: '',
          full: '备品备件管理'
        }
      }
      if (path === '/spare-parts') {
        return {
          level1: '备品备件管理',
          level2: '备品备件管理',
          full: '备品备件管理'
        }
      }
      if (path === '/repair-tools/issue') {
        return {
          level1: '维修工具管理',
          level2: '维修工具领用',
          full: '维修工具管理 / 维修工具领用'
        }
      }
      if (path === '/repair-tools/return') {
        return {
          level1: '维修工具管理',
          level2: '维修工具归还',
          full: '维修工具管理 / 维修工具归还'
        }
      }
      if (path === '/repair-tools/inbound') {
        return {
          level1: '维修工具管理',
          level2: '维修工具库存',
          full: '维修工具管理 / 维修工具库存'
        }
      }
      if (path === '/maintenance-log/fill') {
        return {
          level1: '维保日志',
          level2: '新报维保日志',
          full: '维保日志 / 新报维保日志'
        }
      }
      if (path === '/maintenance-log/list') {
        return {
          level1: '维保日志',
          level2: '维保日志查询',
          full: '维保日志 / 维保日志查询'
        }
      }
      if (path === '/weekly-report/fill') {
        return {
          level1: '维保日志',
          level2: '新报部门周报',
          full: '维保日志 / 新报部门周报'
        }
      }
      if (path === '/weekly-report/list') {
        return {
          level1: '维保日志',
          level2: '部门周报查询',
          full: '维保日志 / 部门周报查询'
        }
      }
      return {
        level1: '维保项目管理',
        level2: '项目信息管理',
        full: '维保项目管理 / 项目信息管理'
      }
    })

    const toggleMenu = (menuId: string) => {
      if (expandedMenus.value.includes(menuId)) {
        expandedMenus.value = expandedMenus.value.filter(id => id !== menuId)
      } else {
        expandedMenus.value = [...expandedMenus.value, menuId]
      }
    }

    const handleMenuClick = (item: MenuItem) => {
      activeMenu.value = item.id
      const parentMenu = menuItems.find(menu => menu.children && menu.children.some(child => child.id === item.id))
      if (parentMenu && parentMenu.id) {
        if (!expandedMenus.value.includes(parentMenu.id)) {
          expandedMenus.value = [...expandedMenus.value, parentMenu.id]
        }
      }
      console.log('Navigate to', item.id, 'path=', item.path)
      if (item.path) {
        router.push({ path: item.path })
      } else if (item.id === 'near-expiry-alert') {
        router.push('/near-expiry-alert')
      }
    }

    const showUserMenu = ref(false)
    const userList = ref<User[]>([])

    const loadUserList = async () => {
      try {
        const response = await personnelService.getAll()
        if (response.code === 200 && response.data) {
          userList.value = response.data.map((p: any) => ({
            id: p.id,
            name: p.name,
            role: p.role,
            department: p.department || '',
            phone: p.phone || ''
          }))
        }
      } catch (error) {
        console.error('加载用户列表失败:', error)
      }
    }

    const selectUser = (user: User) => {
      userStore.setUser(user)
      showUserMenu.value = false
      
      const currentPath = route.path
      const menuId = getRouteMenuId(currentPath)
      if (menuId && !canShowMenu(menuId)) {
        navigateToFirstAllowedRoute()
      }
    }

    const getRouteMenuId = (path: string): string | null => {
      for (const menu of menuItems) {
        if (menu.path === path) {
          return menu.id
        }
        if (menu.children) {
          const child = menu.children.find(c => c.path === path)
          if (child) {
            return child.id
          }
        }
      }
      return null
    }

    const navigateToFirstAllowedRoute = () => {
      for (const menu of menuItems) {
        if (menu.path && canShowMenu(menu.id)) {
          router.push(menu.path)
          return
        }
        if (menu.children) {
          for (const child of menu.children) {
            if (child.path && canShowMenu(child.id)) {
              router.push(child.path)
              return
            }
          }
        }
      }
      router.push('/project-info')
    }

    onMounted(async () => {
      await loadUserList()
      
      const storedUser = userStore.getUser()
      if (!storedUser && userList.value.length > 0) {
        userStore.setUser(userList.value[0])
      }
    })

    return {
      filteredMenuItems,
      expandedMenus,
      activeMenu,
      currentBreadcrumb,
      toggleMenu,
      handleMenuClick,
      isFullscreenMode,
      currentUser: userStore.readonlyCurrentUser,
      userInitials,
      userDisplayName,
      showUserMenu,
      userList,
      selectUser
    }
  }
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
  background: #001F3F;
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

.menu-item {
  padding: 10px 16px;
  cursor: pointer;
  transition: background 0.15s;
  font-size: 18px;
}

.menu-item:hover {
  background: rgba(255, 255, 255, 0.08);
}

.menu-item.active {
  background: rgba(255, 255, 255, 0.1);
  border-left: 3px solid #90caf9;
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
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.submenu-item:hover {
  background: rgba(255, 255, 255, 0.06);
}

.submenu-item.active {
  background: rgba(255, 255, 255, 0.08);
  border-left: 3px solid #90caf9;
  font-weight: 500;
}

.main-content {
  flex: 1;
  background: #f8f9fa;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.center-content {
  padding: 0;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: #F5F7FA;
  border-bottom: 1px solid #e0e0e0;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.breadcrumb-level1 {
  color: #1976d2;
  font-weight: 500;
}

.breadcrumb-separator {
  color: #999;
}

.breadcrumb-level2 {
  color: #333;
  font-weight: 600;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 12px;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  position: relative;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1976d2 0%, #42a5f5 100%);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-name {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.dropdown-arrow {
  font-size: 10px;
  color: #999;
  margin-left: 4px;
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  min-width: 180px;
  max-height: 300px;
  overflow-y: auto;
  z-index: 1000;
}

.dropdown-item {
  padding: 10px 16px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: background 0.15s;
  border-bottom: 1px solid #f0f0f0;
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover {
  background: #f5f5f5;
}

.dropdown-item.active {
  background: #e3f2fd;
  color: #1976d2;
  font-weight: 500;
}

.content-wrapper {
  padding: 20px;
  max-width: 100%;
  margin: 0 auto;
  flex: 1;
}

.layout.fullscreen-mode .content-wrapper {
  padding: 0;
}

.layout.fullscreen-mode .main-content {
  background: #f5f7fa;
}
</style>
