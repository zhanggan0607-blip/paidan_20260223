import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import Layout from '@/components/Layout.vue'
import LoginPage from '@/views/LoginPage.vue'
import ProjectInfoManagement from '@/views/ProjectInfoManagement.vue'
import MaintenancePlanManagement from '@/views/MaintenancePlanManagement.vue'
import OverdueAlert from '@/views/OverdueAlert.vue'
import InspectionItemPage from '@/views/InspectionItemPage.vue'
import NearExpiryReminders from '@/views/NearExpiryReminders.vue'
import TemporaryRepairDetail from '@/views/TemporaryRepairDetail.vue'
import PeriodicInspectionQuery from '@/views/PeriodicInspectionQuery.vue'
import SpotWorkDetail from '@/views/SpotWorkDetail.vue'
import PersonnelManagement from '@/views/PersonnelManagement.vue'
import StatisticsPage from '@/views/StatisticsPage.vue'
import TemporaryRepairQuery from '@/views/TemporaryRepairQuery.vue'
import SpotWorkManagement from '@/views/SpotWorkManagement.vue'
import SparePartsManagement from '@/views/SparePartsManagement.vue'
import SparePartsIssue from '@/views/SparePartsIssue.vue'
import SparePartsStock from '@/views/SparePartsStock.vue'
import WorkPlanManagement from '@/views/WorkPlanManagement.vue'
import CustomerManagement from '@/views/CustomerManagement.vue'
import RepairToolsIssue from '@/views/RepairToolsIssue.vue'
import RepairToolsInbound from '@/views/RepairToolsInbound.vue'
import { authService } from '@/services/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/project-info'
      },
      {
        path: 'statistics',
        component: StatisticsPage
      },
      {
        path: 'project-info',
        component: ProjectInfoManagement
      },
      {
        path: 'maintenance-plan',
        component: MaintenancePlanManagement
      },
      {
        path: 'overdue-alert',
        component: OverdueAlert
      },
      {
        path: 'inspection-item',
        component: InspectionItemPage
      },
      {
        path: 'personnel',
        component: PersonnelManagement
      },
      {
        path: 'near-expiry-alert',
        component: NearExpiryReminders
      },
      {
        path: 'work-order/temporary-repair',
        component: TemporaryRepairQuery
      },
      {
        path: 'work-order/temporary-repair/detail',
        name: 'TemporaryRepairDetail',
        component: TemporaryRepairDetail
      },
      {
        path: 'work-order/periodic-inspection',
        component: PeriodicInspectionQuery
      },
      {
        path: 'work-order/spot-work',
        component: SpotWorkManagement
      },
      {
        path: 'work-order/spot-work/detail',
        name: 'SpotWorkDetail',
        component: SpotWorkDetail
      },
      {
        path: 'spare-parts',
        component: SparePartsManagement
      },
      {
        path: 'spare-parts/issue',
        component: SparePartsIssue
      },
      {
        path: 'spare-parts/stock',
        component: SparePartsStock
      },
      {
        path: 'work-plan',
        component: WorkPlanManagement
      },
      {
        path: 'customer',
        component: CustomerManagement
      },
      {
        path: 'repair-tools/issue',
        component: RepairToolsIssue
      },
      {
        path: 'repair-tools/inbound',
        component: RepairToolsInbound
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
