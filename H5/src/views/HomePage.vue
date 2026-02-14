<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../utils/api'
import type { ApiResponse } from '../types'

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

const fetchStatistics = async () => {
  loading.value = true
  try {
    const response = await api.get<unknown, ApiResponse<Statistics>>('/work-plan/statistics')
    if (response.success) {
      statistics.value = response.data
    }
  } catch (error) {
    console.error('Failed to fetch statistics:', error)
  } finally {
    loading.value = false
  }
}

const statCards = computed(() => [
  { key: 'expiringSoon', label: '临期工单', value: statistics.value.expiringSoon, color: '#ff976a', route: '/work-list?type=expiring' },
  { key: 'overdue', label: '超期工单', value: statistics.value.overdue, color: '#ee0a24', route: '/work-list?type=overdue', showBadge: hasOverdue.value },
  { key: 'yearlyCompleted', label: '本年完成', value: statistics.value.yearlyCompleted, color: '#07c160', route: '/work-list?type=completed' },
  { key: 'periodicInspection', label: '定期巡检单', value: statistics.value.periodicInspection, color: '#1989fa', route: '/work-list?type=periodic' },
  { key: 'temporaryRepair', label: '临时维修单', value: statistics.value.temporaryRepair, color: '#7232dd', route: '/work-list?type=repair' },
  { key: 'spotWork', label: '零星用工单', value: statistics.value.spotWork, color: '#ff976a', route: '/work-list?type=spot' }
])

const quickActions = [
  { key: 'periodic', label: '定期巡检', icon: 'todo-list-o', color: '#1989fa', route: '/periodic-inspection' },
  { key: 'repair', label: '临时维修', icon: 'warning-o', color: '#ff976a', route: '/temporary-repair' },
  { key: 'spot', label: '零星用工', icon: 'cluster-o', color: '#07c160', route: '/spot-work' }
]

const handleCardClick = (card: { route: string }) => {
  router.push(card.route)
}

const handleQuickAction = (action: { route: string }) => {
  router.push(action.route)
}

const handleQuickFill = () => {
  router.push('/spot-work/quick-fill')
}

const handleBack = () => {
  router.back()
}

onMounted(() => {
  fetchStatistics()
})
</script>

<template>
  <div class="home-page">
    <van-nav-bar title="SSTCP维保系统" fixed placeholder>
      <template #left>
        <van-icon name="arrow-left" @click="handleBack" />
      </template>
    </van-nav-bar>
    
    <div class="content">
      <div class="actions-section">
        <van-grid :column-num="3" :border="false">
          <van-grid-item 
            v-for="action in quickActions" 
            :key="action.key"
            :text="action.label"
            @click="handleQuickAction(action)"
          >
            <template #icon>
              <van-icon :name="action.icon" :color="action.color" size="28" />
            </template>
          </van-grid-item>
        </van-grid>
      </div>

      <div class="quick-fill-section">
        <van-cell-group inset>
          <van-cell title="快捷填报" is-link @click="handleQuickFill">
            <template #icon>
              <van-icon name="edit" class="quick-fill-icon" />
            </template>
            <template #label>
              <span class="quick-fill-label">零星用工快捷填报</span>
            </template>
          </van-cell>
        </van-cell-group>
      </div>

      <div class="statistics-section">
        <van-grid :column-num="3" :border="false">
          <van-grid-item 
            v-for="card in statCards" 
            :key="card.key"
            @click="handleCardClick(card)"
          >
            <template #text>
              <div class="stat-card">
                <div class="stat-value" :style="{ color: card.color }">
                  {{ card.value }}
                  <van-badge v-if="card.showBadge" dot class="overdue-badge" />
                </div>
                <div class="stat-label">{{ card.label }}</div>
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

.quick-fill-section {
  margin-bottom: 12px;
}

.quick-fill-icon {
  font-size: 20px;
  color: #1989fa;
  margin-right: 8px;
}

.quick-fill-label {
  color: #969799;
  font-size: 12px;
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
}

.stat-label {
  font-size: 12px;
  color: #646566;
  margin-top: 4px;
}

.overdue-badge {
  position: absolute;
  top: -4px;
  right: -8px;
}

:deep(.van-cell-group--inset) {
  margin: 0;
}

:deep(.van-grid-item__content) {
  padding: 16px 8px;
}
</style>
