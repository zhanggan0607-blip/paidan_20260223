import { useRouter, useRoute } from 'vue-router'

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

export const useNavigation = () => {
  const router = useRouter()
  const route = useRoute()

  const goBack = (extraQuery?: Record<string, string>) => {
    const fromPath = route.query.from as string
    if (fromPath) {
      router.push(fromPath)
      return
    }

    const currentRouteName = route.name as string
    const parentRouteName = parentPageMap[currentRouteName]

    if (parentRouteName) {
      const query: Record<string, string> = {}
      if (route.query.tab !== undefined) {
        query.tab = route.query.tab as string
      }
      if (extraQuery) {
        Object.assign(query, extraQuery)
      }
      router.push({ name: parentRouteName, query: Object.keys(query).length > 0 ? query : undefined })
    } else {
      router.push({ name: 'Home' })
    }
  }

  return {
    goBack,
  }
}
