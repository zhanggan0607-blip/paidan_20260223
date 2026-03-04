import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import Layout from '@/components/Layout.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: Layout,
    children: [
      {
        path: '',
        redirect: '/project-info'
      },
      {
        path: 'statistics',
        component: () => import('@/views/StatisticsPage.vue')
      },
      {
        path: 'project-info',
        component: () => import('@/views/ProjectInfoManagement.vue')
      },
      {
        path: 'maintenance-plan',
        component: () => import('@/views/MaintenancePlanManagement.vue')
      },
      {
        path: 'overdue-alert',
        component: () => import('@/views/OverdueAlert.vue')
      },
      {
        path: 'inspection-item',
        component: () => import('@/views/InspectionItemPage.vue')
      },
      {
        path: 'personnel',
        component: () => import('@/views/PersonnelManagement.vue')
      },
      {
        path: 'near-expiry-alert',
        component: () => import('@/views/NearExpiryReminders.vue')
      },
      {
        path: 'work-order/temporary-repair',
        component: () => import('@/views/TemporaryRepairQuery.vue')
      },
      {
        path: 'work-order/temporary-repair/detail',
        name: 'TemporaryRepairDetail',
        component: () => import('@/views/TemporaryRepairDetail.vue')
      },
      {
        path: 'work-order/periodic-inspection',
        component: () => import('@/views/PeriodicInspectionQuery.vue')
      },
      {
        path: 'work-order/spot-work',
        component: () => import('@/views/SpotWorkManagement.vue')
      },
      {
        path: 'work-order/spot-work/detail',
        name: 'SpotWorkDetail',
        component: () => import('@/views/SpotWorkDetail.vue')
      },
      {
        path: 'spare-parts',
        component: () => import('@/views/SparePartsManagement.vue')
      },
      {
        path: 'spare-parts/issue',
        component: () => import('@/views/SparePartsIssue.vue')
      },
      {
        path: 'spare-parts/stock',
        component: () => import('@/views/SparePartsStock.vue')
      },
      {
        path: 'spare-parts/return',
        component: () => import('@/views/SparePartsReturn.vue')
      },
      {
        path: 'work-plan',
        component: () => import('@/views/WorkPlanManagement.vue')
      },
      {
        path: 'customer',
        component: () => import('@/views/CustomerManagement.vue')
      },
      {
        path: 'repair-tools/issue',
        component: () => import('@/views/RepairToolsIssue.vue')
      },
      {
        path: 'repair-tools/return',
        component: () => import('@/views/RepairToolsReturn.vue')
      },
      {
        path: 'repair-tools/inbound',
        component: () => import('@/views/RepairToolsInbound.vue')
      },
      {
        path: 'maintenance-log/fill',
        component: () => import('@/views/MaintenanceLogFill.vue')
      },
      {
        path: 'maintenance-log/list',
        component: () => import('@/views/MaintenanceLogList.vue')
      },
      {
        path: 'weekly-report/fill',
        component: () => import('@/views/WeeklyReportFill.vue')
      },
      {
        path: 'weekly-report/list',
        component: () => import('@/views/WeeklyReportList.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  next()
})

export default router
