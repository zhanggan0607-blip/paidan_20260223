import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { MenuItem } from '@/types'
import { useUserStore } from '@/stores/userStore'

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

export function useMenu() {
  const router = useRouter()
  const route = useRoute()
  const userStore = useUserStore()
  const expandedMenus = ref<string[]>(['statistics'])
  const activeMenu = ref<string>('project-info')

  const canShowMenu = (menuId: string): boolean => {
    if (!userStore.currentUser) return false
    return userStore.canShowMenu(menuId)
  }

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

  return {
    menuItems,
    filteredMenuItems,
    expandedMenus,
    activeMenu,
    currentBreadcrumb,
    toggleMenu,
    handleMenuClick,
  }
}
