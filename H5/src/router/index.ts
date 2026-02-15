import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomePage.vue'),
    meta: { title: '运维人员_手机端' }
  },
  {
    path: '/project-info',
    name: 'ProjectInfo',
    component: () => import('../views/ProjectInfoPage.vue'),
    meta: { title: '项目信息' }
  },
  {
    path: '/work-list',
    name: 'WorkList',
    component: () => import('../views/WorkListPage.vue'),
    meta: { title: '工单列表' }
  },
  {
    path: '/periodic-inspection',
    name: 'PeriodicInspection',
    component: () => import('../views/PeriodicInspectionPage.vue'),
    meta: { title: '定期巡检' }
  },
  {
    path: '/periodic-inspection/:id',
    name: 'PeriodicInspectionDetail',
    component: () => import('../views/PeriodicInspectionDetailPage.vue'),
    meta: { title: '定期巡检详情' }
  },
  {
    path: '/temporary-repair',
    name: 'TemporaryRepair',
    component: () => import('../views/TemporaryRepairPage.vue'),
    meta: { title: '临时维修' }
  },
  {
    path: '/spot-work',
    name: 'SpotWork',
    component: () => import('../views/SpotWorkPage.vue'),
    meta: { title: '零星用工' }
  },
  {
    path: '/spot-work/quick-fill',
    name: 'SpotWorkQuickFill',
    component: () => import('../views/SpotWorkQuickFillPage.vue'),
    meta: { title: '零星用工快捷填报' }
  },
  {
    path: '/signature',
    name: 'Signature',
    component: () => import('../views/SignaturePage.vue'),
    meta: { title: '签字确认' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  document.title = (to.meta.title as string) || 'SSTCP维保系统'
  next()
})

export default router
