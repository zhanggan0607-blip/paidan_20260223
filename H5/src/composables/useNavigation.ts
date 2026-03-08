/**
 * 导航组合式函数
 * 统一管理页面导航逻辑
 */
import { useRouter, useRoute } from 'vue-router'

/**
 * 页面父级路由映射
 * 定义每个页面的上一层页面
 */
const parentPageMap: Record<string, string> = {
  ProjectInfo: 'Home',
  WorkList: 'Home',
  PeriodicInspection: 'Home',
  PeriodicInspectionDetail: 'PeriodicInspection',
  TemporaryRepair: 'Home',
  TemporaryRepairCreate: 'TemporaryRepair',
  TemporaryRepairDetail: 'TemporaryRepair',
  SpotWork: 'Home',
  SpotWorkDetail: 'SpotWork',
  SpotWorkQuickFill: 'SpotWork',
  WorkerEntry: 'SpotWork',
  Signature: 'Home',
  SpotWorkApply: 'SpotWork',
  MaintenanceLog: 'Home',
  MaintenanceLogList: 'Home',
  MaintenanceLogDetail: 'MaintenanceLogList',
  WeeklyReportFill: 'Home',
  WeeklyReportList: 'Home',
  WeeklyReportDetail: 'WeeklyReportList',
  WeeklyReportAll: 'Home',
  SparePartsIssue: 'Home',
  SparePartsStock: 'Home',
  SparePartsReturn: 'Home',
  RepairToolsIssue: 'Home',
  RepairToolsStock: 'Home',
  RepairToolsReturn: 'Home',
}

/**
 * 导航组合式函数
 * @returns 导航相关的方法
 */
export const useNavigation = () => {
  const router = useRouter()
  const route = useRoute()

  /**
   * 返回上一层页面，根据路由层级直接返回，不依赖浏览器历史记录
   */
  const goBack = () => {
    const currentRouteName = route.name as string
    const parentRouteName = parentPageMap[currentRouteName]

    if (parentRouteName) {
      router.push({ name: parentRouteName })
    } else {
      router.push({ name: 'Home' })
    }
  }

  /**
   * 返回工单列表页
   * @param workOrderType 工单类型
   */
  const goBackToWorkList = (
    workOrderType: 'periodic_inspection' | 'temporary_repair' | 'spot_work'
  ) => {
    const paths: Record<string, string> = {
      periodic_inspection: '/periodic-inspection',
      temporary_repair: '/temporary-repair',
      spot_work: '/spot-work',
    }
    router.push(paths[workOrderType] || '/')
  }

  /**
   * 跳转到签名页面
   * @param fromPath 来源路径
   * @param type 签名类型
   */
  const goToSignature = (fromPath: string, type: string = 'default') => {
    router.push({
      path: '/signature',
      query: {
        from: fromPath,
        type,
      },
    })
  }

  /**
   * 跳转到工单详情页
   * @param workOrderType 工单类型
   * @param id 工单ID
   * @param options 额外选项
   */
  const goToWorkDetail = (
    workOrderType: 'periodic_inspection' | 'temporary_repair' | 'spot_work',
    id: number,
    options?: { tab?: number; mode?: string }
  ) => {
    const paths: Record<string, string> = {
      periodic_inspection: '/periodic-inspection',
      temporary_repair: '/temporary-repair',
      spot_work: '/spot-work',
    }

    const query: Record<string, any> = {}
    if (options?.tab !== undefined) {
      query.tab = options.tab
    }
    if (options?.mode) {
      query.mode = options.mode
    }

    router.push({
      path: `${paths[workOrderType]}/${id}`,
      query,
    })
  }

  /**
   * 跳转到首页
   */
  const goToHome = () => {
    router.push('/')
  }

  return {
    goBack,
    goBackToWorkList,
    goToSignature,
    goToWorkDetail,
    goToHome,
  }
}
