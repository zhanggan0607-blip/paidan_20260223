import { createRouter, createWebHistory } from 'vue-router'
import { authService } from '../services/auth'

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
    meta: { title: '项目信息', permission: 'canViewProjectInfo' }
  },
  {
    path: '/work-list',
    name: 'WorkList',
    component: () => import('../views/WorkListPage.vue'),
    meta: { title: '工单列表', permission: 'canViewWorkList' }
  },
  {
    path: '/periodic-inspection',
    name: 'PeriodicInspection',
    component: () => import('../views/PeriodicInspectionPage.vue'),
    meta: { title: '定期巡检', permission: 'canViewPeriodicInspection' }
  },
  {
    path: '/periodic-inspection/:id',
    name: 'PeriodicInspectionDetail',
    component: () => import('../views/PeriodicInspectionDetailPage.vue'),
    meta: { title: '定期巡检详情', permission: 'canViewPeriodicInspection' }
  },
  {
    path: '/temporary-repair',
    name: 'TemporaryRepair',
    component: () => import('../views/TemporaryRepairPage.vue'),
    meta: { title: '临时维修', permission: 'canViewTemporaryRepair' }
  },
  {
    path: '/temporary-repair/:id',
    name: 'TemporaryRepairDetail',
    component: () => import('../views/TemporaryRepairDetailPage.vue'),
    meta: { title: '临时维修详情', permission: 'canViewTemporaryRepair' }
  },
  {
    path: '/spot-work',
    name: 'SpotWork',
    component: () => import('../views/SpotWorkPage.vue'),
    meta: { title: '零星用工', permission: 'canViewSpotWork' }
  },
  {
    path: '/spot-work/:id',
    name: 'SpotWorkDetail',
    component: () => import('../views/SpotWorkDetailPage.vue'),
    meta: { title: '零星用工详情', permission: 'canViewSpotWork' }
  },
  {
    path: '/spot-work/quick-fill',
    name: 'SpotWorkQuickFill',
    component: () => import('../views/SpotWorkQuickFillPage.vue'),
    meta: { title: '申报用工', permission: 'canQuickFillSpotWork' }
  },
  {
    path: '/spot-work/worker-entry',
    name: 'WorkerEntry',
    component: () => import('../views/WorkerEntryPage.vue'),
    meta: { title: '施工人员录入', permission: 'canQuickFillSpotWork' }
  },
  {
    path: '/signature',
    name: 'Signature',
    component: () => import('../views/SignaturePage.vue'),
    meta: { title: '签字确认', permission: 'canViewSignature' }
  },
  {
    path: '/spot-work-apply',
    name: 'SpotWorkApply',
    component: () => import('../views/SpotWorkApplyPage.vue'),
    meta: { title: '申报用工', permission: 'canQuickFillSpotWork' }
  },
  {
    path: '/maintenance-log',
    name: 'MaintenanceLog',
    component: () => import('../views/MaintenanceLogFillPage.vue'),
    meta: { title: '维保日志填报', permission: 'canFillMaintenanceLog' }
  },
  {
    path: '/maintenance-log-list',
    name: 'MaintenanceLogList',
    component: () => import('../views/MaintenanceLogPage.vue'),
    meta: { title: '已填报日志', permission: 'canViewMaintenanceLog' }
  },
  {
    path: '/maintenance-log-detail/:id',
    name: 'MaintenanceLogDetail',
    component: () => import('../views/MaintenanceLogDetailPage.vue'),
    meta: { title: '维保日志详情', permission: 'canViewMaintenanceLogDetail' }
  },
  {
    path: '/maintenance-log-all',
    name: 'MaintenanceLogAll',
    component: () => import('../views/MaintenanceLogAllPage.vue'),
    meta: { title: '查看维保日志', permission: 'canViewAllMaintenanceLog' }
  },
  {
    path: '/weekly-report',
    name: 'WeeklyReportFill',
    component: () => import('../views/WeeklyReportFillPage.vue'),
    meta: { title: '部门周报填报', permission: 'canViewDepartmentWeeklyReport' }
  },
  {
    path: '/weekly-report-list',
    name: 'WeeklyReportList',
    component: () => import('../views/WeeklyReportListPage.vue'),
    meta: { title: '已报部门周报', permission: 'canViewDepartmentWeeklyReport' }
  },
  {
    path: '/weekly-report-all',
    name: 'WeeklyReportAll',
    component: () => import('../views/WeeklyReportAllPage.vue'),
    meta: { title: '查看部门周报', permission: 'canViewAllWeeklyReport' }
  },
  {
    path: '/weekly-report-detail/:id',
    name: 'WeeklyReportDetail',
    component: () => import('../views/WeeklyReportDetailPage.vue'),
    meta: { title: '部门周报详情', permission: 'canViewAllWeeklyReport' }
  },
  {
    path: '/spare-parts-issue',
    name: 'SparePartsIssue',
    component: () => import('../views/SparePartsIssuePage.vue'),
    meta: { title: '备品备件领用', permission: 'canViewSparePartsIssue' }
  },
  {
    path: '/spare-parts-stock',
    name: 'SparePartsStock',
    component: () => import('../views/SparePartsStockPage.vue'),
    meta: { title: '配品备件入库', permission: 'canViewSparePartsStock' }
  },
  {
    path: '/repair-tools-issue',
    name: 'RepairToolsIssue',
    component: () => import('../views/RepairToolsIssuePage.vue'),
    meta: { title: '维修工具领用', permission: 'canViewRepairToolsIssue' }
  },
  {
    path: '/repair-tools-stock',
    name: 'RepairToolsStock',
    component: () => import('../views/RepairToolsStockPage.vue'),
    meta: { title: '维修工具库存', permission: 'canViewRepairToolsInbound' }
  },
  {
    path: '/repair-tools-return',
    name: 'RepairToolsReturn',
    component: () => import('../views/RepairToolsReturnPage.vue'),
    meta: { title: '维修工具归还', permission: 'canViewRepairToolsIssue' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  document.title = (to.meta.title as string) || 'SSTCP维保系统'
  
  if (to.meta.permission) {
    const user = authService.getCurrentUser()
    const permissionMethod = to.meta.permission as string
    if (typeof (authService as any)[permissionMethod] === 'function') {
      if (!(authService as any)[permissionMethod](user)) {
        next({ name: 'Home' })
        return
      }
    }
  }
  
  next()
})

export default router
