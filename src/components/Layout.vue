<template>
  <div class="layout">
    <aside class="sidebar">
        <div class="sidebar-header">
          <h1 class="system-title">SSTCP维保系统</h1>
        </div>
       <nav class="sidebar-nav">
         <div
           v-for="menu in menuItems"
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
        <div class="top-bar">
        <div class="breadcrumb">
          <span class="breadcrumb-level1">{{ currentBreadcrumb.level1 }}</span>
          <span class="breadcrumb-separator" v-if="currentBreadcrumb.level2">/</span>
          <span class="breadcrumb-level2">{{ currentBreadcrumb.level2 }}</span>
        </div>
        <div class="user-info">
          <div class="user-avatar">MO</div>
          <span class="user-name">momo.zxy</span>
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
import { defineComponent, ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { MenuItem } from '@/types'

export default defineComponent({
  name: 'Layout',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const expandedMenus = ref<string[]>(['statistics'])
    const activeMenu = ref<string>('project-info')

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
            { id: 'work-plan', label: '工作计划管理', path: '/work-plan' },
            { id: 'temporary-repair', label: '临时维修单查询', path: '/work-order/temporary-repair' },
            { id: 'spot-work', label: '零星用工管理', path: '/work-order/spot-work' }
          ]
        },
        {
          id: 'spare-parts',
          label: '备品备件管理',
          children: [
            { id: 'spare-parts-inventory', label: '备品备件库存', path: '/spare-parts/inventory' },
            { id: 'spare-parts-issue', label: '备品备件领用', path: '/spare-parts/issue' },
            { id: 'spare-parts-stock', label: '备品备件入库', path: '/spare-parts/stock' }
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
          level2: '零星用工管理',
          full: '工单管理 / 零星用工管理'
        }
      }
      if (path === '/work-plan') {
        return {
          level1: '工单管理',
          level2: '工作计划管理',
          full: '工单管理 / 工作计划管理'
        }
      }
      if (path === '/spare-parts/issue') {
        return {
          level1: '备品备件管理',
          level2: '备品备件领用',
          full: '备品备件管理 / 备品备件领用'
        }
      }
      if (path === '/spare-parts/stock') {
        return {
          level1: '备品备件管理',
          level2: '备品备件入库',
          full: '备品备件管理 / 备品备件入库'
        }
      }
      if (path === '/spare-parts/inventory') {
        return {
          level1: '备品备件管理',
          level2: '备品备件库存',
          full: '备品备件管理 / 备品备件库存'
        }
      }
      if (path === '/spare-parts') {
        return {
          level1: '备品备件管理',
          level2: '备品备件管理',
          full: '备品备件管理'
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

    return {
      menuItems,
      expandedMenus,
      activeMenu,
      currentBreadcrumb,
      toggleMenu,
      handleMenuClick
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
  gap: 12px;
  padding: 6px 12px;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
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

.content-wrapper {
  padding: 20px;
  max-width: 100%;
  margin: 0 auto;
  flex: 1;
}

</style>
