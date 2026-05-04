import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import Layout from '@/components/Layout.vue'
import { useUserStore } from '@/stores/userStore'
import { canShowMenu, getDefaultPath } from '@/config/permission'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginPage.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/change-password',
    name: 'ChangePassword',
    component: () => import('@/views/ChangePasswordPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Home',
        redirect: '/project-info',
      },
      {
        path: 'statistics',
        name: 'Statistics',
        component: () => import('@/views/StatisticsPage.vue'),
        meta: { permission: 'statistics' },
      },
      {
        path: 'project-info',
        name: 'ProjectInfo',
        component: () => import('@/views/ProjectInfoManagement.vue'),
        meta: { permission: 'project-info' },
      },
      {
        path: 'maintenance-plan',
        name: 'MaintenancePlan',
        component: () => import('@/views/MaintenancePlanManagement.vue'),
        meta: { permission: 'project-info' },
      },
      {
        path: 'overdue-alert',
        name: 'OverdueAlert',
        component: () => import('@/views/OverdueAlert.vue'),
        meta: { permission: 'overdue-alert' },
      },
      {
        path: 'inspection-item',
        name: 'InspectionItem',
        component: () => import('@/views/InspectionItemPage.vue'),
        meta: { permission: 'inspection-item' },
      },
      {
        path: 'personnel',
        name: 'Personnel',
        component: () => import('@/views/PersonnelManagement.vue'),
        meta: { permission: 'personnel' },
      },
      {
        path: 'near-expiry-alert',
        name: 'NearExpiryAlert',
        component: () => import('@/views/NearExpiryReminders.vue'),
        meta: { permission: 'near-expiry-alert' },
      },
      {
        path: 'work-order/temporary-repair',
        name: 'TemporaryRepair',
        component: () => import('@/views/TemporaryRepairQuery.vue'),
        meta: { permission: 'temporary-repair' },
      },
      {
        path: 'work-order/temporary-repair/detail',
        name: 'TemporaryRepairDetail',
        component: () => import('@/views/TemporaryRepairDetail.vue'),
        meta: { permission: 'temporary-repair' },
      },
      {
        path: 'work-order/periodic-inspection',
        name: 'PeriodicInspection',
        component: () => import('@/views/PeriodicInspectionQuery.vue'),
        meta: { permission: 'periodic-inspection' },
      },
      {
        path: 'work-order/spot-work',
        name: 'SpotWork',
        component: () => import('@/views/SpotWorkManagement.vue'),
        meta: { permission: 'spot-work' },
      },
      {
        path: 'work-order/spot-work/detail',
        name: 'SpotWorkDetail',
        component: () => import('@/views/SpotWorkDetail.vue'),
        meta: { permission: 'spot-work' },
      },
      {
        path: 'spare-parts',
        name: 'SpareParts',
        component: () => import('@/views/SparePartsManagement.vue'),
        meta: { permission: 'spare-parts' },
      },
      {
        path: 'spare-parts/issue',
        name: 'SparePartsIssue',
        component: () => import('@/views/SparePartsIssue.vue'),
        meta: { permission: 'spare-parts-issue' },
      },
      {
        path: 'spare-parts/stock',
        name: 'SparePartsStock',
        component: () => import('@/views/SparePartsStock.vue'),
        meta: { permission: 'spare-parts-stock' },
      },
      {
        path: 'spare-parts/return',
        name: 'SparePartsReturn',
        component: () => import('@/views/SparePartsReturn.vue'),
        meta: { permission: 'spare-parts-issue' },
      },
      {
        path: 'work-plan',
        name: 'WorkPlan',
        component: () => import('@/views/WorkPlanManagement.vue'),
        meta: { permission: 'work-plan' },
      },
      {
        path: 'customer',
        name: 'Customer',
        component: () => import('@/views/CustomerManagement.vue'),
        meta: { permission: 'customer' },
      },
      {
        path: 'repair-tools/issue',
        name: 'RepairToolsIssue',
        component: () => import('@/views/RepairToolsIssue.vue'),
        meta: { permission: 'repair-tools-issue' },
      },
      {
        path: 'repair-tools/return',
        name: 'RepairToolsReturn',
        component: () => import('@/views/RepairToolsReturn.vue'),
        meta: { permission: 'repair-tools-issue' },
      },
      {
        path: 'repair-tools/inbound',
        name: 'RepairToolsInbound',
        component: () => import('@/views/RepairToolsInbound.vue'),
        meta: { permission: 'repair-tools-inbound' },
      },
      {
        path: 'maintenance-log/fill',
        name: 'MaintenanceLogFill',
        component: () => import('@/views/MaintenanceLogFill.vue'),
        meta: { permission: 'maintenance-log-fill' },
      },
      {
        path: 'maintenance-log/list',
        name: 'MaintenanceLogList',
        component: () => import('@/views/MaintenanceLogList.vue'),
        meta: { permission: 'maintenance-log-list' },
      },
      {
        path: 'weekly-report/fill',
        name: 'WeeklyReportFill',
        component: () => import('@/views/WeeklyReportFill.vue'),
        meta: { permission: 'weekly-report-fill' },
      },
      {
        path: 'weekly-report/list',
        name: 'WeeklyReportList',
        component: () => import('@/views/WeeklyReportList.vue'),
        meta: { permission: 'weekly-report-list' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, _from, next) => {
  const store = useUserStore()
  const token = store.token
  const user = store.currentUser
  const requiresAuth = to.meta.requiresAuth !== false

  if (token && !user) {
    await store.validateToken()
  }

  const currentToken = store.token
  const currentUser = store.currentUser

  if (requiresAuth && !currentToken) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  if (to.path === '/' && currentToken && currentUser) {
    next({ path: getDefaultPath((currentUser as { role?: string }).role) })
    return
  }

  if (to.path === '/login' && currentToken && currentUser) {
    next({ path: getDefaultPath((currentUser as { role?: string }).role) })
    return
  }

  if (
    currentToken &&
    currentUser &&
    (currentUser as { must_change_password?: boolean }).must_change_password &&
    to.path !== '/change-password'
  ) {
    next({ name: 'ChangePassword' })
    return
  }

  const permission = to.meta.permission as string | undefined
  if (permission && currentUser) {
    const role = (currentUser as { role?: string }).role
    if (!canShowMenu(permission, role)) {
      next({ path: getDefaultPath(role) })
      return
    }
  }

  next()
})

export default router
