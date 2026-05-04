<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { workPlanService } from '../services'
import { useUserStore } from '../stores/userStore'
const userStore = useUserStore()
import { apiCache, CACHE_KEYS, CACHE_TTL } from '../utils/apiCache'

import { version as appVersion } from '../../package.json'

const router = useRouter()

onMounted(() => {
  fetchStatistics()
})

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
  spotWork: 0,
})

const loading = ref(false)
const hasOverdue = computed(() => statistics.value.overdue > 0)

const fetchStatistics = async (forceRefresh = false) => {
  loading.value = true
  try {
    const cacheKey = CACHE_KEYS.STATISTICS
    
    if (!forceRefresh) {
      const cached = apiCache.get<Statistics>(cacheKey)
      if (cached) {
        statistics.value = cached
        loading.value = false
        return
      }
    }
    
    const response = await workPlanService.getStatistics()
    if (response.code === 200) {
      statistics.value = response.data
      apiCache.set(cacheKey, response.data, CACHE_TTL.MEDIUM)
    }
  } catch (error) {
    console.error('Failed to fetch statistics:', error)
  } finally {
    loading.value = false
  }
}

const currentYear = new Date().getFullYear()

const statCards = computed(() => {
  const cards = [
    {
      key: 'expiringSoon',
      label: '临期工单',
      year: `${currentYear}年度`,
      value: statistics.value.expiringSoon,
      color: 'var(--color-warning)',
      bg: 'var(--color-warning-subtle)',
      route: '/work-list?type=expiring',
      show: userStore.canViewWorkOrder(),
    },
    {
      key: 'overdue',
      label: '超期工单',
      year: `${currentYear}年度`,
      value: statistics.value.overdue,
      color: 'var(--color-danger)',
      bg: 'var(--color-danger-subtle)',
      route: '/work-list?type=overdue',
      showBadge: hasOverdue.value,
      show: userStore.canViewWorkOrder(),
    },
    {
      key: 'yearlyCompleted',
      label: '已完成',
      year: `${currentYear}年度`,
      value: statistics.value.yearlyCompleted,
      color: 'var(--color-success)',
      bg: 'var(--color-success-subtle)',
      route: '/work-list?type=completed',
      show: userStore.canViewWorkOrder(),
    },
    {
      key: 'periodicInspection',
      label: '定期巡检单',
      year: `${currentYear}年度`,
      value: statistics.value.periodicInspection,
      color: 'var(--color-primary)',
      bg: 'var(--color-primary-subtle)',
      route: '/work-list?type=periodic',
      show: userStore.canViewPeriodicInspection(),
    },
    {
      key: 'temporaryRepair',
      label: '临时维修单',
      year: `${currentYear}年度`,
      value: statistics.value.temporaryRepair,
      color: 'var(--color-info)',
      bg: 'var(--color-info-subtle)',
      route: '/work-list?type=repair',
      show: userStore.canViewTemporaryRepair(),
    },
    {
      key: 'spotWork',
      label: '零星用工单',
      year: `${currentYear}年度`,
      value: statistics.value.spotWork,
      color: 'var(--color-accent)',
      bg: 'var(--color-accent-subtle)',
      route: '/work-list?type=spot',
      show: userStore.canViewSpotWork(),
    },
  ]
  return cards.filter((card) => card.show)
})

const quickActions = computed(() => {
  const actions = [
    {
      key: 'periodic',
      label: '定期巡检',
      icon: 'todo-list-o',
      color: 'var(--color-primary)',
      bg: 'var(--color-primary-subtle)',
      route: '/periodic-inspection',
      show: userStore.canViewPeriodicInspection(),
    },
    {
      key: 'repair',
      label: '临时维修',
      icon: 'warning-o',
      color: 'var(--color-accent)',
      bg: 'var(--color-accent-subtle)',
      route: '/temporary-repair',
      show: userStore.canViewTemporaryRepair(),
    },
    {
      key: 'spot',
      label: '申报用工',
      icon: 'cluster-o',
      color: 'var(--color-success)',
      bg: 'var(--color-success-subtle)',
      route: '/spot-work-apply',
      show: userStore.canApplySpotWork(),
    },
    {
      key: 'newLog',
      label: '新报维保日志',
      icon: 'edit',
      color: 'var(--color-info)',
      bg: 'var(--color-info-subtle)',
      route: '/maintenance-log',
      show: userStore.canFillMaintenanceLog(),
    },
    {
      key: 'historyLog',
      label: '维保日志查询',
      icon: 'description',
      color: 'var(--color-primary)',
      bg: 'var(--color-primary-subtle)',
      route: '/maintenance-log-list',
      show: userStore.canViewMaintenanceLog() || userStore.canViewAllMaintenanceLog(),
    },
    {
      key: 'weeklyReport',
      label: '新报部门周报',
      icon: 'calendar-o',
      color: 'var(--color-info)',
      bg: 'var(--color-info-subtle)',
      route: '/weekly-report',
      show: userStore.isDepartmentManager,
    },
    {
      key: 'weeklyHistory',
      label: '已报部门周报',
      icon: 'description',
      color: 'var(--color-primary)',
      bg: 'var(--color-primary-subtle)',
      route: '/weekly-report-list',
      show: userStore.isDepartmentManager,
    },
    {
      key: 'viewWeekly',
      label: '查看部门周报',
      icon: 'calendar-o',
      color: 'var(--color-info)',
      bg: 'var(--color-info-subtle)',
      route: '/weekly-report-all',
      show: userStore.isAdmin,
    },
    {
      key: 'sparePartsIssue',
      label: '备品备件领用',
      icon: 'shopping-cart-o',
      color: 'var(--color-primary)',
      bg: 'var(--color-primary-subtle)',
      route: '/spare-parts-issue',
      show: userStore.canViewSparePartsIssue(),
    },
    {
      key: 'sparePartsReturn',
      label: '备品备件归还',
      icon: 'back-top',
      color: 'var(--color-success)',
      bg: 'var(--color-success-subtle)',
      route: '/spare-parts-return',
      show: userStore.canViewSparePartsIssue(),
    },
    {
      key: 'sparePartsStock',
      label: '备品备件库存',
      icon: 'logistics',
      color: 'var(--color-success)',
      bg: 'var(--color-success-subtle)',
      route: '/spare-parts-stock',
      show: userStore.canViewSparePartsStock(),
    },
    {
      key: 'repairToolsIssue',
      label: '维修工具领用',
      icon: 'setting-o',
      color: 'var(--color-accent)',
      bg: 'var(--color-accent-subtle)',
      route: '/repair-tools-issue',
      show: userStore.canViewRepairToolsIssue(),
    },
    {
      key: 'repairToolsReturn',
      label: '维修工具归还',
      icon: 'back-top',
      color: 'var(--color-success)',
      bg: 'var(--color-success-subtle)',
      route: '/repair-tools-return',
      show: userStore.canViewRepairToolsIssue(),
    },
    {
      key: 'repairToolsStock',
      label: '维修工具库存',
      icon: 'bag-o',
      color: 'var(--color-info)',
      bg: 'var(--color-info-subtle)',
      route: '/repair-tools-stock',
      show: userStore.canViewRepairToolsStock(),
    },
  ]
  return actions.filter((action) => action.show)
})

const handleQuickAction = (action: { route: string }) => {
  router.push(action.route)
}

const handleCardClick = (card: { route: string }) => {
  router.push(card.route)
}

const handleRefresh = () => {
  return fetchStatistics(true)
}
</script>

<template>
  <div class="home-page">
    <div class="home-header">
      <div class="header-grid"></div>
      <div class="header-content">
        <div class="greeting">
          <span class="greeting-text">{{ userStore.currentUser?.name || '用户' }}</span>
          <span class="greeting-label">，您好</span>
        </div>
        <div class="header-year">{{ currentYear }} 年度概览</div>
      </div>
      <div class="header-version">V{{ appVersion }}</div>
    </div>

    <van-pull-refresh v-model="loading" @refresh="handleRefresh">
      <div class="content">
        <div class="section-title">工单统计</div>
        <div class="statistics-grid">
          <div
            v-for="card in statCards"
            :key="card.key"
            class="stat-card"
            :class="{ 'stat-card--active': card.value > 0 }"
            @click="handleCardClick(card)"
          >
            <div class="stat-value" :style="{ color: card.color }">
              {{ card.value }}
              <van-badge v-if="card.showBadge" dot class="overdue-badge" />
            </div>
            <div class="stat-label">{{ card.label }}</div>
            <div class="stat-year">{{ card.year }}</div>
          </div>
        </div>

        <div class="section-title">快捷操作</div>
        <div class="actions-grid">
          <div
            v-for="action in quickActions"
            :key="action.key"
            class="action-item"
            @click="handleQuickAction(action)"
          >
            <div class="action-icon" :style="{ background: action.bg }">
              <van-icon :name="action.icon" :color="action.color" size="22" />
            </div>
            <div class="action-label">{{ action.label }}</div>
          </div>
        </div>
      </div>
    </van-pull-refresh>
  </div>
</template>

<style scoped>
.home-page {
  min-height: 100vh;
  background-color: var(--color-bg-page);
}

.home-header {
  position: relative;
  background: var(--color-nav-bg);
  padding: 20px 20px 28px;
  overflow: hidden;
}

.header-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(42, 122, 122, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(42, 122, 122, 0.06) 1px, transparent 1px);
  background-size: 20px 20px;
}

.header-content {
  position: relative;
}

.greeting {
  margin-bottom: 4px;
}

.greeting-text {
  font-size: var(--text-xl);
  font-weight: var(--weight-bold);
  color: var(--color-nav-text-active);
}

.greeting-label {
  font-size: var(--text-md);
  color: var(--color-nav-text);
}

.header-year {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-primary);
  letter-spacing: 0.06em;
  margin-top: 2px;
}

.content {
  padding: var(--space-4);
  padding-top: var(--space-5);
}

.section-title {
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  color: var(--color-text-primary);
  letter-spacing: 0.04em;
  margin-bottom: var(--space-3);
  padding-left: 2px;
}

.statistics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-3);
  margin-bottom: var(--space-6);
}

.stat-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  box-shadow: var(--shadow-xs);
  transition: box-shadow var(--transition-normal), transform var(--transition-fast);
}

.stat-card--active {
  box-shadow: var(--shadow-sm);
}

.stat-card:active {
  transform: scale(0.97);
}

.stat-value {
  font-family: var(--font-mono);
  font-size: var(--text-3xl);
  font-weight: var(--weight-bold);
  line-height: 1;
  margin-bottom: var(--space-2);
  position: relative;
}

.stat-label {
  font-size: var(--text-sm);
  color: var(--color-text-regular);
  font-weight: var(--weight-medium);
}

.stat-year {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--color-text-placeholder);
  margin-top: 2px;
  letter-spacing: 0.02em;
}

.overdue-badge {
  position: absolute;
  top: -2px;
  right: -6px;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-3);
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-1);
  border-radius: var(--radius-md);
  transition: background var(--transition-fast);
}

.action-item:active {
  background: var(--color-primary-subtle);
}

.action-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-label {
  font-size: 11px;
  color: var(--color-text-regular);
  text-align: center;
  line-height: 1.3;
  font-weight: var(--weight-medium);
}

.header-version {
  position: absolute;
  right: 20px;
  bottom: 8px;
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--color-nav-text);
  opacity: 0.4;
  letter-spacing: 0.06em;
}
</style>
