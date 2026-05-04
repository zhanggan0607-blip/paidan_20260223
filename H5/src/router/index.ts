/**
 * H5端路由配置
 *
 * 路由守卫逻辑：
 * 1. /login页面不需要认证
 * 2. 无token时跳转登录页，携带redirect参数
 * 3. must_change_password为true时强制跳转修改密码页
 * 4. 根据meta.permission检查用户权限
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/userStore'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginPage.vue'),
    meta: { title: '登录' },
  },
  {
    path: '/change-password',
    name: 'ChangePassword',
    component: () => import('../views/ChangePasswordPage.vue'),
    meta: { title: '修改密码' },
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomePage.vue'),
    meta: { title: '运维人员_手机端' },
  },
  {
    path: '/project-info',
    name: 'ProjectInfo',
    component: () => import('../views/ProjectInfoPage.vue'),
    meta: { title: '项目信息', permission: 'canViewProjectInfo' },
  },
  {
    path: '/work-list',
    name: 'WorkList',
    component: () => import('../views/WorkListPage.vue'),
    meta: { title: '工单列表', permission: 'canViewWorkList' },
  },
  {
    path: '/periodic-inspection',
    name: 'PeriodicInspection',
    component: () => import('../views/PeriodicInspectionPage.vue'),
    meta: { title: '定期巡检', permission: 'canViewPeriodicInspection' },
  },
  {
    path: '/periodic-inspection/:id',
    name: 'PeriodicInspectionDetail',
    component: () => import('../views/PeriodicInspectionDetailPage.vue'),
    meta: { title: '定期巡检详情', permission: 'canViewPeriodicInspection' },
  },
  {
    path: '/temporary-repair',
    name: 'TemporaryRepair',
    component: () => import('../views/TemporaryRepairPage.vue'),
    meta: { title: '临时维修', permission: 'canViewTemporaryRepair' },
  },
  {
    path: '/temporary-repair/create',
    name: 'TemporaryRepairCreate',
    component: () => import('../views/TemporaryRepairCreatePage.vue'),
    meta: { title: '新增临时维修单', permission: 'canViewTemporaryRepair' },
  },
  {
    path: '/temporary-repair/:id',
    name: 'TemporaryRepairDetail',
    component: () => import('../views/TemporaryRepairDetailPage.vue'),
    meta: { title: '临时维修详情', permission: 'canViewTemporaryRepair' },
  },
  {
    path: '/spot-work',
    name: 'SpotWork',
    component: () => import('../views/SpotWorkPage.vue'),
    meta: { title: '零星用工', permission: 'canViewSpotWork' },
  },
  {
    path: '/spot-work/:id',
    name: 'SpotWorkDetail',
    component: () => import('../views/SpotWorkDetailPage.vue'),
    meta: { title: '零星用工详情', permission: 'canViewSpotWork' },
  },
  {
    path: '/spot-work/quick-fill',
    name: 'SpotWorkQuickFill',
    component: () => import('../views/SpotWorkQuickFillPage.vue'),
    meta: { title: '申报用工', permission: 'canQuickFillSpotWork' },
  },
  {
    path: '/spot-work/worker-entry',
    name: 'WorkerEntry',
    component: () => import('../views/WorkerEntryPage.vue'),
    meta: { title: '施工人员录入', permission: 'canQuickFillSpotWork' },
  },
  {
    path: '/signature',
    name: 'Signature',
    component: () => import('../views/SignaturePage.vue'),
    meta: { title: '签字确认', permission: 'canViewSignature' },
  },
  {
    path: '/spot-work-apply',
    name: 'SpotWorkApply',
    component: () => import('../views/SpotWorkApplyPage.vue'),
    meta: { title: '申报用工', permission: 'canQuickFillSpotWork' },
  },
  {
    path: '/maintenance-log',
    name: 'MaintenanceLog',
    component: () => import('../views/MaintenanceLogFillPage.vue'),
    meta: { title: '维保日志填报', permission: 'canFillMaintenanceLog' },
  },
  {
    path: '/maintenance-log-list',
    name: 'MaintenanceLogList',
    component: () => import('../views/MaintenanceLogPage.vue'),
    meta: { title: '维保日志查询', permission: 'canViewMaintenanceLog' },
  },
  {
    path: '/maintenance-log-detail/:id',
    name: 'MaintenanceLogDetail',
    component: () => import('../views/MaintenanceLogDetailPage.vue'),
    meta: { title: '维保日志详情', permission: 'canViewMaintenanceLogDetail' },
  },
  {
    path: '/weekly-report',
    name: 'WeeklyReportFill',
    component: () => import('../views/WeeklyReportFillPage.vue'),
    meta: { title: '部门周报填报', permission: 'canViewDepartmentWeeklyReport' },
  },
  {
    path: '/weekly-report-list',
    name: 'WeeklyReportList',
    component: () => import('../views/WeeklyReportListPage.vue'),
    meta: { title: '部门周报查询', permission: 'canViewDepartmentWeeklyReport' },
  },
  {
    path: '/weekly-report-detail/:id',
    name: 'WeeklyReportDetail',
    component: () => import('../views/WeeklyReportDetailPage.vue'),
    meta: { title: '部门周报详情', permission: 'canViewAllWeeklyReport' },
  },
  {
    path: '/weekly-report-all',
    name: 'WeeklyReportAll',
    component: () => import('../views/WeeklyReportAllPage.vue'),
    meta: { title: '查看部门周报', permission: 'isAdmin' },
  },
  {
    path: '/spare-parts-issue',
    name: 'SparePartsIssue',
    component: () => import('../views/SparePartsIssuePage.vue'),
    meta: { title: '备品备件领用', permission: 'canViewSparePartsIssue' },
  },
  {
    path: '/spare-parts-stock',
    name: 'SparePartsStock',
    component: () => import('../views/SparePartsStockPage.vue'),
    meta: { title: '备品备件入库', permission: 'canViewSparePartsStock' },
  },
  {
    path: '/spare-parts-return',
    name: 'SparePartsReturn',
    component: () => import('../views/SparePartsReturnPage.vue'),
    meta: { title: '备品备件归还', permission: 'canViewSparePartsIssue' },
  },
  {
    path: '/repair-tools-issue',
    name: 'RepairToolsIssue',
    component: () => import('../views/RepairToolsIssuePage.vue'),
    meta: { title: '维修工具领用', permission: 'canViewRepairToolsIssue' },
  },
  {
    path: '/repair-tools-stock',
    name: 'RepairToolsStock',
    component: () => import('../views/RepairToolsStockPage.vue'),
    meta: { title: '维修工具库存', permission: 'canViewRepairToolsInbound' },
  },
  {
    path: '/repair-tools-return',
    name: 'RepairToolsReturn',
    component: () => import('../views/RepairToolsReturnPage.vue'),
    meta: { title: '维修工具归还', permission: 'canViewRepairToolsIssue' },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFoundPage.vue'),
    meta: { title: '页面不存在' },
  },
]

const router = createRouter({
  history: createWebHistory('/h5/'),
  routes,
})

router.beforeEach(async (to, _from, next) => {
  document.title = (to.meta.title as string) || 'SSTCP维保系统'

  if (to.path === '/login' || to.path === '/change-password') {
    next()
    return
  }

  const userStore = useUserStore()

  if (!userStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  const user = userStore.currentUser
  if (
    user &&
    (user as { must_change_password?: boolean }).must_change_password &&
    to.path !== '/change-password'
  ) {
    next({ name: 'ChangePassword' })
    return
  }

  if (to.meta.permission) {
    const permissionKey = to.meta.permission as string
    const permValue = (userStore as any)[permissionKey]
    if (typeof permValue === 'function') {
      if (!permValue()) {
        next({ name: 'Home' })
        return
      }
    } else if (typeof permValue === 'boolean') {
      if (!permValue) {
        next({ name: 'Home' })
        return
      }
    }
  }

  next()
})

export default router
