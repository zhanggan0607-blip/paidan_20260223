import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import Layout from '@/components/Layout.vue'
import ProjectInfoManagement from '@/views/ProjectInfoManagement.vue'
import MaintenancePlanManagement from '@/views/Maintenance-plan-management.vue'
import OverdueAlert from '@/views/OverdueAlert.vue'
import InspectionItemPage from '@/views/InspectionItemPage.vue'
import NearExpiryReminders from '@/views/NearExpiryReminders.vue'
import TemporaryRepairDetail from '@/views/TemporaryRepairDetail.vue'
import PeriodicInspectionDetail from '@/views/PeriodicInspectionDetail.vue'
import SpotWorkDetail from '@/views/SpotWorkDetail.vue'

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
        path: '/project-info',
        component: ProjectInfoManagement
      },
      {
        path: '/maintenance-plan',
        component: MaintenancePlanManagement
      },
      {
        path: '/overdue-alert',
        component: OverdueAlert
      },
      {
        path: '/inspection-item',
        component: InspectionItemPage
      }
      ,
      {
        path: '/near-expiry-alert',
        component: NearExpiryReminders
      },
      {
        path: '/work-order/temporary-repair',
        component: TemporaryRepairDetail
      },
      {
        path: '/work-order/periodic-inspection',
        component: PeriodicInspectionDetail
      },
      {
        path: '/work-order/spot-work',
        component: SpotWorkDetail
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
