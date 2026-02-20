<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import UserSelector from '../components/UserSelector.vue'
import { authService, type User } from '../services/auth'

const router = useRouter()

interface Statistics {
  expiringSoon: number
  overdue: number
  yearlyCompleted: number
  periodicInspection: number
  temporaryRepair: number
  spotWork: number
}

const statistics = ref<Statistics>({
  expiringSoon: 0,
  overdue: 0,
  yearlyCompleted: 0,
  periodicInspection: 0,
  temporaryRepair: 0,
  spotWork: 0
})

const loading = ref(false)
const hasOverdue = computed(() => statistics.value.overdue > 0)
const currentUser = ref<User | null>(null)

const fetchStatistics = async () => {
  loading.value = true
  try {
    const response = await api.get<unknown, ApiResponse<Statistics>>('/work-plan/statistics')
    if (response.code === 200) {
      statistics.value = response.data
    }
  } catch (error) {
    console.error('Failed to fetch statistics:', error)
  } finally {
    loading.value = false
  }
}

const handleUserChanged = () => {
  currentUser.value = authService.getCurrentUser()
  fetchStatistics()
}

const currentYear = new Date().getFullYear()

const statCards = computed(() => {
  const user = currentUser.value
  const cards = [
    { key: 'expiringSoon', label: '临期工单', year: `${currentYear}年度`, value: statistics.value.expiringSoon, color: '#ff976a', route: '/work-list?type=expiring', show: authService.canViewWorkOrder(user) },
    { key: 'overdue', label: '超期工单', year: `${currentYear}年度`, value: statistics.value.overdue, color: '#ee0a24', route: '/work-list?type=overdue', showBadge: hasOverdue.value, show: authService.canViewWorkOrder(user) },
    { key: 'yearlyCompleted', label: '已完成', year: `${currentYear}年度`, value: statistics.value.yearlyCompleted, color: '#07c160', route: '/work-list?type=completed', show: authService.canViewWorkOrder(user) },
    { key: 'periodicInspection', label: '定期巡检单', year: `${currentYear}年度`, value: statistics.value.periodicInspection, color: '#1989fa', route: '/work-list?type=periodic', show: authService.canViewPeriodicInspection(user) },
    { key: 'temporaryRepair', label: '临时维修单', year: `${currentYear}年度`, value: statistics.value.temporaryRepair, color: '#7232dd', route: '/work-list?type=repair', show: authService.canViewTemporaryRepair(user) },
    { key: 'spotWork', label: '零星用工单', year: `${currentYear}年度`, value: statistics.value.spotWork, color: '#ff976a', route: '/work-list?type=spot', show: authService.canViewSpotWork(user) }
  ]
  return cards.filter(card => card.show)
})

const quickActions = computed(() => {
  const user = currentUser.value
  const actions = [
    { key: 'periodic', label: '定期巡检', icon: 'todo-list-o', color: '#1989fa', route: '/periodic-inspection', show: authService.canViewPeriodicInspection(user) },
    { key: 'repair', label: '临时维修', icon: 'warning-o', color: '#ff976a', route: '/temporary-repair', show: authService.canViewTemporaryRepair(user) },
    { key: 'spot', label: '申报用工', icon: 'cluster-o', color: '#07c160', route: '/spot-work-apply', show: authService.canApplySpotWork(user) },
    { key: 'newLog', label: '新报维保日志', icon: 'edit', color: '#7232dd', route: '/maintenance-log', show: authService.canFillMaintenanceLog(user) },
    { key: 'historyLog', label: '已报维保日志', icon: 'description', color: '#1989fa', route: '/maintenance-log-list', show: authService.canViewMaintenanceLog(user) && !authService.isAdmin(user) && !authService.isDepartmentManager(user) },
    { key: 'weeklyReport', label: '新报部门周报', icon: 'calendar-o', color: '#7232dd', route: '/weekly-report', show: authService.isDepartmentManager(user) },
    { key: 'weeklyHistory', label: '已报部门周报', icon: 'description', color: '#1989fa', route: '/weekly-report-list', show: authService.isDepartmentManager(user) },
    { key: 'viewAllLog', label: '查看维保日志', icon: 'eye-o', color: '#07c160', route: '/maintenance-log-all', show: authService.canViewAllMaintenanceLog(user) },
    { key: 'viewWeekly', label: '查看部门周报', icon: 'calendar-o', color: '#7232dd', route: '/weekly-report-all', show: authService.isAdmin(user) },
    { key: 'sparePartsIssue', label: '备品备件领用', icon: 'shopping-cart-o', color: '#1989fa', route: '/spare-parts-issue', show: authService.canViewSparePartsIssue(user) },
    { key: 'sparePartsStock', label: '备品备件库存', icon: 'logistics', color: '#07c160', route: '/spare-parts-stock', show: authService.canViewSparePartsStock(user) },
    { key: 'repairToolsIssue', label: '维修工具领用', icon: 'setting-o', color: '#ff976a', route: '/repair-tools-issue', show: authService.canViewRepairToolsIssue(user) },
    { key: 'repairToolsReturn', label: '维修工具归还', icon: 'back-top', color: '#07c160', route: '/repair-tools-return', show: authService.canViewRepairToolsIssue(user) },
    { key: 'repairToolsStock', label: '维修工具库存', icon: 'bag-o', color: '#7232dd', route: '/repair-tools-stock', show: authService.canViewRepairToolsStock(user) }
  ]
  return actions.filter(action => action.show)
})

const handleQuickAction = (action: { route: string }) => {
  router.push(action.route)
}

const handleCardClick = (card: { route: string }) => {
  router.push(card.route)
}

onMounted(() => {
  currentUser.value = authService.getCurrentUser()
  fetchStatistics()
})
</script>

<template>
  <div class="home-page">
    <van-nav-bar title="SSTCP维保系统" fixed placeholder>
      <template #right>
        <UserSelector @userChanged="handleUserChanged" />
      </template>
    </van-nav-bar>
    
    <div class="content">
      <div class="actions-section">
        <van-grid :column-num="2" :border="false">
          <van-grid-item 
            v-for="action in quickActions" 
            :key="action.key"
            :text="action.label"
            @click="handleQuickAction(action)"
          >
            <template #icon>
              <van-icon :name="action.icon" :color="action.color" size="32" />
            </template>
          </van-grid-item>
        </van-grid>
      </div>

      <div class="statistics-section">
        <van-grid :column-num="2" :border="false">
          <van-grid-item 
            v-for="card in statCards" 
            :key="card.key"
            @click="handleCardClick(card)"
            :class="{ 'stat-item-highlight': card.value > 0 }"
          >
            <template #text>
              <div class="stat-card">
                <div class="stat-value" :style="{ color: card.color }" :class="{ 'has-value': card.value > 0 }">
                  {{ card.value }}
                  <van-badge v-if="card.showBadge" dot class="overdue-badge" />
                </div>
                <div class="stat-label">{{ card.label }}</div>
                <div class="stat-year">{{ card.year }}</div>
              </div>
            </template>
          </van-grid-item>
        </van-grid>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.content {
  padding: 12px;
  padding-top: 0;
}

.actions-section {
  margin-bottom: 12px;
}

.statistics-section {
  margin-bottom: 12px;
}

.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 0;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  position: relative;
  transition: transform 0.2s ease;
}

.stat-value.has-value {
  transform: scale(1.1);
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-label {
  font-size: 12px;
  color: #646566;
  margin-top: 4px;
}

.stat-year {
  font-size: 10px;
  color: #999;
  margin-top: 2px;
}

.overdue-badge {
  position: absolute;
  top: -4px;
  right: -8px;
}

:deep(.van-grid-item__content) {
  padding: 16px 8px;
}

:deep(.van-grid-item.stat-item-highlight .van-grid-item__content) {
  background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(240,245,255,0.9) 100%);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}
</style>
