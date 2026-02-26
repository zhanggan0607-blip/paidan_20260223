<script setup lang="ts">
/**
 * 首页组件
 * 展示工单统计信息和快捷操作入口
 */
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import UserSelector from '../components/UserSelector.vue'
import { userStore, type User } from '../stores/userStore'

const router = useRouter()

/** 统计数据接口 */
interface Statistics {
  /** 临期工单数 */
  expiringSoon: number
  /** 超期工单数 */
  overdue: number
  /** 年度已完成数 */
  yearlyCompleted: number
  /** 定期巡检单数 */
  periodicInspection: number
  /** 临时维修单数 */
  temporaryRepair: number
  /** 零星用工单数 */
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

/**
 * 获取统计数据
 * 从后端获取工单统计信息
 */
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

/**
 * 处理用户切换事件
 * 切换用户后重新获取统计数据
 * @param _user 切换后的用户信息
 */
const handleUserChanged = (_user: User) => {
  fetchStatistics()
}

/**
 * 处理用户加载完成事件
 * 用户加载完成后获取统计数据
 * @param _user 加载完成的用户信息
 */
const handleUserReady = (_user: User) => {
  fetchStatistics()
}

const currentYear = new Date().getFullYear()

/**
 * 统计卡片配置
 * 根据用户权限过滤显示的卡片
 */
const statCards = computed(() => {
  const cards = [
    { key: 'expiringSoon', label: '临期工单', year: `${currentYear}年度`, value: statistics.value.expiringSoon, color: '#ff976a', route: '/work-list?type=expiring', show: userStore.canViewWorkOrder() },
    { key: 'overdue', label: '超期工单', year: `${currentYear}年度`, value: statistics.value.overdue, color: '#ee0a24', route: '/work-list?type=overdue', showBadge: hasOverdue.value, show: userStore.canViewWorkOrder() },
    { key: 'yearlyCompleted', label: '已完成', year: `${currentYear}年度`, value: statistics.value.yearlyCompleted, color: '#07c160', route: '/work-list?type=completed', show: userStore.canViewWorkOrder() },
    { key: 'periodicInspection', label: '定期巡检单', year: `${currentYear}年度`, value: statistics.value.periodicInspection, color: '#1989fa', route: '/work-list?type=periodic', show: userStore.canViewPeriodicInspection() },
    { key: 'temporaryRepair', label: '临时维修单', year: `${currentYear}年度`, value: statistics.value.temporaryRepair, color: '#7232dd', route: '/work-list?type=repair', show: userStore.canViewTemporaryRepair() },
    { key: 'spotWork', label: '零星用工单', year: `${currentYear}年度`, value: statistics.value.spotWork, color: '#ff976a', route: '/work-list?type=spot', show: userStore.canViewSpotWork() }
  ]
  return cards.filter(card => card.show)
})

/**
 * 快捷操作配置
 * 根据用户权限过滤显示的操作项
 */
const quickActions = computed(() => {
  const actions = [
    { key: 'periodic', label: '定期巡检', icon: 'todo-list-o', color: '#1989fa', route: '/periodic-inspection', show: userStore.canViewPeriodicInspection() },
    { key: 'repair', label: '临时维修', icon: 'warning-o', color: '#ff976a', route: '/temporary-repair', show: userStore.canViewTemporaryRepair() },
    { key: 'spot', label: '申报用工', icon: 'cluster-o', color: '#07c160', route: '/spot-work-apply', show: userStore.canApplySpotWork() },
    { key: 'newLog', label: '新报维保日志', icon: 'edit', color: '#7232dd', route: '/maintenance-log', show: userStore.canFillMaintenanceLog() },
    { key: 'historyLog', label: '维保日志查询', icon: 'description', color: '#1989fa', route: '/maintenance-log-list', show: userStore.canViewMaintenanceLog() || userStore.canViewAllMaintenanceLog() },
    { key: 'weeklyReport', label: '新报部门周报', icon: 'calendar-o', color: '#7232dd', route: '/weekly-report', show: userStore.isDepartmentManager() },
    { key: 'weeklyHistory', label: '已报部门周报', icon: 'description', color: '#1989fa', route: '/weekly-report-list', show: userStore.isDepartmentManager() },
    { key: 'viewWeekly', label: '查看部门周报', icon: 'calendar-o', color: '#7232dd', route: '/weekly-report-all', show: userStore.isAdmin() },
    { key: 'sparePartsIssue', label: '备品备件领用', icon: 'shopping-cart-o', color: '#1989fa', route: '/spare-parts-issue', show: userStore.canViewSparePartsIssue() },
    { key: 'sparePartsReturn', label: '备品备件归还', icon: 'back-top', color: '#07c160', route: '/spare-parts-return', show: userStore.canViewSparePartsIssue() },
    { key: 'sparePartsStock', label: '备品备件库存', icon: 'logistics', color: '#07c160', route: '/spare-parts-stock', show: userStore.canViewSparePartsStock() },
    { key: 'repairToolsIssue', label: '维修工具领用', icon: 'setting-o', color: '#ff976a', route: '/repair-tools-issue', show: userStore.canViewRepairToolsIssue() },
    { key: 'repairToolsReturn', label: '维修工具归还', icon: 'back-top', color: '#07c160', route: '/repair-tools-return', show: userStore.canViewRepairToolsIssue() },
    { key: 'repairToolsStock', label: '维修工具库存', icon: 'bag-o', color: '#7232dd', route: '/repair-tools-stock', show: userStore.canViewRepairToolsStock() }
  ]
  return actions.filter(action => action.show)
})

/**
 * 处理快捷操作点击
 * @param action 操作配置对象
 */
const handleQuickAction = (action: { route: string }) => {
  router.push(action.route)
}

/**
 * 处理统计卡片点击
 * @param card 卡片配置对象
 */
const handleCardClick = (card: { route: string }) => {
  router.push(card.route)
}
</script>

<template>
  <div class="home-page">
    <van-nav-bar title="SSTCP维保系统" fixed placeholder>
      <template #right>
        <UserSelector @userChanged="handleUserChanged" @ready="handleUserReady" />
      </template>
    </van-nav-bar>
    
    <div class="content">
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
