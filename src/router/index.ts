import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import Layout from '@/components/Layout.vue'
import { userStore } from '@/stores/userStore'
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
        redirect: '/project-info',
      },
      {
        path: 'statistics',
        component: () => import('@/views/StatisticsPage.vue'),
        meta: { permission: 'statistics' },
      },
      {
        path: 'project-info',
        component: () => import('@/views/ProjectInfoManagement.vue'),
        meta: { permission: 'project-info' },
      },
      {
        path: 'maintenance-plan',
        component: () => import('@/views/MaintenancePlanManagement.vue'),
        meta: { permission: 'project-info' },
      },
      {
        path: 'overdue-alert',
        component: () => import('@/views/OverdueAlert.vue'),
        meta: { permission: 'overdue-alert' },
      },
      {
        path: 'inspection-item',
        component: () => import('@/views/InspectionItemPage.vue'),
        meta: { permission: 'inspection-item' },
      },
      {
        path: 'personnel',
        component: () => import('@/views/PersonnelManagement.vue'),
        meta: { permission: 'personnel' },
      },
      {
        path: 'near-expiry-alert',
        component: () => import('@/views/NearExpiryReminders.vue'),
        meta: { permission: 'near-expiry-alert' },
      },
      {
        path: 'work-order/temporary-repair',
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
        component: () => import('@/views/SparePartsManagement.vue'),
        meta: { permission: 'spare-parts' },
      },
      {
        path: 'spare-parts/issue',
        component: () => import('@/views/SparePartsIssue.vue'),
        meta: { permission: 'spare-parts-issue' },
      },
      {
        path: 'spare-parts/stock',
        component: () => import('@/views/SparePartsStock.vue'),
        meta: { permission: 'spare-parts-stock' },
      },
      {
        path: 'spare-parts/return',
        component: () => import('@/views/SparePartsReturn.vue'),
        meta: { permission: 'spare-parts-issue' },
      },
      {
        path: 'work-plan',
        component: () => import('@/views/WorkPlanManagement.vue'),
        meta: { permission: 'work-plan' },
      },
      {
        path: 'customer',
        component: () => import('@/views/CustomerManagement.vue'),
        meta: { permission: 'customer' },
      },
      {
        path: 'repair-tools/issue',
        component: () => import('@/views/RepairToolsIssue.vue'),
        meta: { permission: 'repair-tools-issue' },
      },
      {
        path: 'repair-tools/return',
        component: () => import('@/views/RepairToolsReturn.vue'),
        meta: { permission: 'repair-tools-issue' },
      },
      {
        path: 'repair-tools/inbound',
        component: () => import('@/views/RepairToolsInbound.vue'),
        meta: { permission: 'repair-tools-stock' },
      },
      {
        path: 'maintenance-log/fill',
        component: () => import('@/views/MaintenanceLogFill.vue'),
        meta: { permission: 'maintenance-log-fill' },
      },
      {
        path: 'maintenance-log/list',
        component: () => import('@/views/MaintenanceLogList.vue'),
        meta: { permission: 'maintenance-log-list' },
      },
      {
        path: 'weekly-report/fill',
        component: () => import('@/views/WeeklyReportFill.vue'),
        meta: { permission: 'weekly-report-fill' },
      },
      {
        path: 'weekly-report/list',
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

router.beforeEach((to, _from, next) => {
  const token = userStore.getToken()
  const user = userStore.getUser()
  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !token) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  if (to.path === '/' && token && user) {
    next({ path: getDefaultPath((user as { role?: string }).role) })
    return
  }

  if (to.path === '/login' && token && user) {
    next({ path: getDefaultPath((user as { role?: string }).role) })
    return
  }

  if (
    token &&
    user &&
    (user as { must_change_password?: boolean }).must_change_password &&
    to.path !== '/change-password'
  ) {
    next({ name: 'ChangePassword' })
    return
  }

  const permission = to.meta.permission as string | undefined
  if (permission && user) {
    const role = (user as { role?: string }).role
    if (!canShowMenu(permission, role)) {
      next({ path: getDefaultPath(role) })
      return
    }
  }

  next()
})

export default router
