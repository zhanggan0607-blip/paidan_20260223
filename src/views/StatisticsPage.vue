<template>
  <div class="statistics-page">
    <div class="top-bar">
      <div class="menu-toggle" @click="toggleSidebar">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="3" y1="12" x2="21" y2="12"></line>
          <line x1="3" y1="6" x2="21" y2="6"></line>
          <line x1="3" y1="18" x2="21" y2="18"></line>
        </svg>
      </div>
      <div class="year-selector">
        <label class="year-label">年度选择：</label>
        <select class="year-select" v-model="selectedYear" @change="handleYearChange">
          <option v-for="year in availableYears" :key="year" :value="year">
            {{ year }}
          </option>
        </select>
      </div>
      <div class="edit-controls" v-if="isEditMode">
        <button class="btn btn-cancel" @click="cancelEdit">取消</button>
        <button class="btn btn-save" @click="saveConfig" :disabled="saving">
          {{ saving ? '保存中...' : '保存配置' }}
        </button>
      </div>
      <div class="edit-controls" v-else>
        <button class="btn btn-edit" @click="enableEditMode">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 0 0 0-2 2v14a2 2 0 0 0 0 2 2h14a2 2 0 0 0 0 2-2v-7"></path>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1 4"></path>
          </svg>
          编辑布局
        </button>
      </div>
      <div class="user-info">
        <div class="user-avatar">MO</div>
        <span class="user-name">momo.zxy</span>
      </div>
    </div>

    <div class="content" v-if="!loading">
      <div class="cards-section" :class="{ 'edit-mode': isEditMode }">
        <div 
          v-for="card in visibleCards" 
          :key="card.id" 
          class="stat-card"
          :class="getCardClass(card.id)"
          :draggable="isEditMode"
          @dragstart="handleDragStart($event, card, 'card')"
          @dragover="handleDragOver($event)"
          @drop="handleDrop($event, card, 'card')"
        >
          <div class="card-actions" v-if="isEditMode">
            <button class="action-btn" @click="toggleCardVisibility(card.id)">
              {{ card.visible ? '隐藏' : '显示' }}
            </button>
          </div>
          <div class="card-label">{{ getCardLabel(card.id) }}</div>
          <div class="card-value">{{ currentData[getCardDataKey(card.id)] }}</div>
        </div>
      </div>

      <div class="charts-section" :class="{ 'edit-mode': isEditMode }">
        <div class="chart-row" v-for="(chart, rowIndex) in chartRows" :key="rowIndex">
          <div 
            v-for="item in chart" 
            :key="item.id" 
            class="chart-container"
            :class="{ 'hidden': !item.visible }"
            :draggable="isEditMode"
            @dragstart="handleDragStart($event, item, 'chart')"
            @dragover="handleDragOver($event)"
            @drop="handleDrop($event, item, 'chart')"
          >
            <div class="chart-actions" v-if="isEditMode">
              <button class="action-btn" @click="toggleChartVisibility(item.id)">
                {{ item.visible ? '隐藏' : '显示' }}
              </button>
            </div>
            <h3 class="chart-title">{{ getChartTitle(item.id) }}</h3>
            <div v-if="item.id === 'workByPerson'" class="bar-chart horizontal-bar-chart">
              <div v-for="(dataItem, index) in currentData.workOrderByPerson" :key="index" class="bar-item">
                <div class="bar-label">{{ dataItem.name }}</div>
                <div class="bar-wrapper">
                  <div class="bar" :style="{ width: (dataItem.value / maxValue * 100) + '%' }"></div>
                  <div class="bar-value">{{ dataItem.value }}</div>
                </div>
              </div>
            </div>
            <div v-if="item.id === 'inspectionByPerson'" class="bar-chart horizontal-bar-chart">
              <div v-for="(dataItem, index) in currentData.inspectionByPerson" :key="index" class="bar-item">
                <div class="bar-label">{{ dataItem.name }}</div>
                <div class="bar-wrapper">
                  <div class="bar" :style="{ width: (dataItem.value / maxValue * 100) + '%' }"></div>
                  <div class="bar-value">{{ dataItem.value }}</div>
                </div>
              </div>
            </div>
            <div v-if="item.id === 'repairByPerson'" class="bar-chart horizontal-bar-chart">
              <div v-for="(dataItem, index) in currentData.repairByPerson" :key="index" class="bar-item">
                <div class="bar-label">{{ dataItem.name }}</div>
                <div class="bar-wrapper">
                  <div class="bar" :style="{ width: (dataItem.value / maxValue * 100) + '%' }"></div>
                  <div class="bar-value">{{ dataItem.value }}</div>
                </div>
              </div>
            </div>
            <div v-if="item.id === 'laborByPerson'" class="bar-chart horizontal-bar-chart">
              <div v-for="(dataItem, index) in currentData.laborByPerson" :key="index" class="bar-item">
                <div class="bar-label">{{ dataItem.name }}</div>
                <div class="bar-wrapper">
                  <div class="bar" :style="{ width: (dataItem.value / maxValue * 100) + '%' }"></div>
                  <div class="bar-value">{{ dataItem.value }}</div>
                </div>
              </div>
            </div>
            <div v-if="item.id === 'completionRate'" class="pie-chart">
              <div class="pie-chart-container">
                <svg viewBox="0 0 100 100" class="pie-svg">
                  <circle cx="50" cy="50" r="40" fill="none" stroke-width="20"
                    :stroke-dasharray="`${currentData.onTimeRate * 251.2} ${251.2 - currentData.onTimeRate * 251.2}`"
                    stroke="#1976d2"
                    transform="rotate(-90 50 50)"
                  />
                  <circle cx="50" cy="50" r="40" fill="none" stroke-width="20"
                    :stroke-dasharray="`${(1 - currentData.onTimeRate) * 251.2} ${251.2 - (1 - currentData.onTimeRate) * 251.2}`"
                    stroke="#ff9800"
                    transform="rotate(-90 50 50)"
                  />
                </svg>
              </div>
              <div class="pie-legend">
                <div class="legend-item">
                  <div class="legend-color" style="background: #ff9800;"></div>
                  <span>延期完成（{{ Math.round((1 - currentData.onTimeRate) * 100) }}%）</span>
                </div>
                <div class="legend-item">
                  <div class="legend-color" style="background: #1976d2;"></div>
                  <span>预期完成（{{ Math.round(currentData.onTimeRate * 100) }}%）</span>
                </div>
              </div>
            </div>
            <div v-if="item.id === 'topProjects'" class="bar-chart vertical-bar-chart">
              <div class="vertical-bars">
                <div v-for="(dataItem, index) in currentData.topProjects" :key="index" class="vertical-bar-item">
                  <div class="vertical-bar-wrapper">
                    <div class="vertical-bar" :style="{ height: (dataItem.value / maxProjectValue * 100) + '%' }"></div>
                    <div class="vertical-bar-value">{{ dataItem.value }}</div>
                  </div>
                  <div class="vertical-bar-label">{{ dataItem.name }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="loading" v-else>
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onUnmounted, computed } from 'vue'
import { statisticsService, StatisticsOverview, WorkByPerson, CompletionRate, TopProject } from '@/services/statistics'
import { userDashboardConfigService, type DashboardConfig } from '@/services/userDashboardConfig'
import Toast from '@/components/Toast.vue'

export default defineComponent({
  name: 'StatisticsPage',
  components: {
    Toast
  },
  setup() {
    const selectedYear = ref<number>(new Date().getFullYear())
    const availableYears = [2024, 2025, 2026, 2027, 2028]
    const currentData = ref<StatisticsOverview>({
      year: selectedYear.value,
      nearExpiry: 0,
      overdue: 0,
      completed: 0,
      regularInspectionCount: 0,
      temporaryRepairCount: 0,
      spotWorkCount: 0,
      workOrderByPerson: [] as WorkByPerson[],
      inspectionByPerson: [] as WorkByPerson[],
      repairByPerson: [] as WorkByPerson[],
      laborByPerson: [] as WorkByPerson[],
      onTimeRate: 0,
      topProjects: [] as TopProject[]
    })
    const loading = ref<boolean>(false)
    const maxProjectValue = ref<number>(0)
    const isEditMode = ref<boolean>(false)
    const saving = ref<boolean>(false)
    const toast = ref({
      visible: false,
      message: '',
      type: 'success' as 'success' | 'error' | 'warning' | 'info'
    })

    const dashboardConfig = ref<DashboardConfig>({
      cards: [
        { id: 'nearExpiry', visible: true, position: 0 },
        { id: 'overdue', visible: true, position: 1 },
        { id: 'completed', visible: true, position: 2 },
        { id: 'regularInspection', visible: true, position: 3 },
        { id: 'temporaryRepair', visible: true, position: 4 },
        { id: 'spotWork', visible: true, position: 5 }
      ],
      charts: [
        { id: 'workByPerson', visible: true, position: 0 },
        { id: 'inspectionByPerson', visible: true, position: 1 },
        { id: 'repairByPerson', visible: true, position: 2 },
        { id: 'laborByPerson', visible: true, position: 3 },
        { id: 'completionRate', visible: true, position: 4 },
        { id: 'topProjects', visible: true, position: 5 }
      ],
      layout: 'grid'
    })

    const visibleCards = computed(() => {
      return dashboardConfig.value.cards.filter(c => c.visible).sort((a, b) => a.position - b.position)
    })

    const chartRows = computed(() => {
      const charts = dashboardConfig.value.charts.filter(c => c.visible).sort((a, b) => a.position - b.position)
      const rows = []
      for (let i = 0; i < charts.length; i += 2) {
        rows.push(charts.slice(i, i + 2))
      }
      return rows
    })

    const maxValue = computed(() => {
      const allValues = [
        ...currentData.value.workOrderByPerson.map(p => p.value),
        ...currentData.value.inspectionByPerson.map(p => p.value),
        ...currentData.value.repairByPerson.map(p => p.value),
        ...currentData.value.laborByPerson.map(p => p.value)
      ]
      return Math.max(...allValues, 1)
    })

    const getCardClass = (id: string) => {
      const classMap: Record<string, string> = {
        nearExpiry: 'card-near-expiry',
        overdue: 'card-overdue',
        completed: 'card-completed',
        regularInspection: 'card-regular',
        temporaryRepair: 'card-temporary',
        spotWork: 'card-sporadic'
      }
      return classMap[id] || ''
    }

    const getCardLabel = (id: string) => {
      const labelMap: Record<string, string> = {
        nearExpiry: '临期工单',
        overdue: '超期工单',
        completed: '本年完成',
        regularInspection: '定期巡检单',
        temporaryRepair: '临时维修单',
        spotWork: '零星用工单'
      }
      return labelMap[id] || ''
    }

    const getCardDataKey = (id: string) => {
      const keyMap: Record<string, string> = {
        nearExpiry: 'nearExpiry',
        overdue: 'overdue',
        completed: 'completed',
        regularInspection: 'regularInspectionCount',
        temporaryRepair: 'temporaryRepairCount',
        spotWork: 'spotWorkCount'
      }
      return keyMap[id] || ''
    }

    const getChartTitle = (id: string) => {
      const titleMap: Record<string, string> = {
        workByPerson: `本年度工单数量（${selectedYear.value}）`,
        inspectionByPerson: `定期巡检单完成数量（${selectedYear.value}）`,
        repairByPerson: `临时维修单完成数量（${selectedYear.value}）`,
        laborByPerson: `零星用工单完成数量（${selectedYear.value}）`,
        completionRate: `准时完成情况分布（${selectedYear.value}）`,
        topProjects: `临时维修年度前五（${selectedYear.value}）`
      }
      return titleMap[id] || ''
    }

    let abortController: AbortController | null = null
    let draggedItem: any = null
    let draggedType: string = ''

    const toggleSidebar = () => {
    }

    const handleYearChange = async () => {
      if (abortController) {
        abortController.abort()
      }
      abortController = new AbortController()

      loading.value = true
      try {
        const overview = await statisticsService.getStatisticsOverview(selectedYear.value)
        const workByPerson = await statisticsService.getWorkByPerson(selectedYear.value)
        const completionRate = await statisticsService.getCompletionRate(selectedYear.value)
        const topProjects = await statisticsService.getTopProjects(selectedYear.value)

        currentData.value = {
          year: selectedYear.value,
          nearExpiry: overview.nearExpiry,
          overdue: overview.overdue,
          completed: overview.completed,
          regularInspectionCount: overview.regularInspectionCount,
          temporaryRepairCount: overview.temporaryRepairCount,
          spotWorkCount: overview.spotWorkCount,
          workOrderByPerson: workByPerson,
          inspectionByPerson: workByPerson,
          repairByPerson: workByPerson,
          laborByPerson: workByPerson,
          onTimeRate: completionRate.onTimeRate,
          topProjects: topProjects
        }

        maxProjectValue.value = Math.max(...topProjects.map(p => p.value), 0)
      } catch (error) {
        if (error instanceof Error && error.name === 'AbortError') {
          return
        }
      } finally {
        loading.value = false
      }
    }

    const enableEditMode = async () => {
      try {
        const response = await userDashboardConfigService.getConfig('statistics')
        if (response.code === 200 && response.data) {
          dashboardConfig.value = response.data
        }
        isEditMode.value = true
      } catch (error) {
        showToast('加载配置失败', 'error')
      }
    }

    const cancelEdit = () => {
      isEditMode.value = false
      draggedItem = null
      draggedType = ''
    }

    const saveConfig = async () => {
      saving.value = true
      try {
        await userDashboardConfigService.saveConfig('statistics', dashboardConfig.value, 'momo.zxy')
        showToast('配置保存成功', 'success')
        isEditMode.value = false
      } catch (error) {
        showToast('保存配置失败', 'error')
      } finally {
        saving.value = false
      }
    }

    const toggleCardVisibility = (id: string) => {
      const card = dashboardConfig.value.cards.find(c => c.id === id)
      if (card) {
        card.visible = !card.visible
      }
    }

    const toggleChartVisibility = (id: string) => {
      const chart = dashboardConfig.value.charts.find(c => c.id === id)
      if (chart) {
        chart.visible = !chart.visible
      }
    }

    const handleDragStart = (event: DragEvent, item: any, type: string) => {
      draggedItem = item
      draggedType = type
      event.dataTransfer!.effectAllowed = 'move'
    }

    const handleDragOver = (event: DragEvent) => {
      event.preventDefault()
      event.dataTransfer!.dropEffect = 'move'
    }

    const handleDrop = (event: DragEvent, targetItem: any, type: string) => {
      event.preventDefault()
      if (!draggedItem || draggedType !== type) return

      const list = type === 'card' ? dashboardConfig.value.cards : dashboardConfig.value.charts
      const draggedIndex = list.findIndex(i => i.id === draggedItem.id)
      const targetIndex = list.findIndex(i => i.id === targetItem.id)

      if (draggedIndex !== -1 && targetIndex !== -1) {
        const [removed] = list.splice(draggedIndex, 1)
        list.splice(targetIndex, 0, removed)
      }

      draggedItem = null
      draggedType = ''
    }

    const showToast = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'success') => {
      toast.value.message = message
      toast.value.type = type
      toast.value.visible = true
      setTimeout(() => {
        toast.value.visible = false
      }, 3000)
    }

    onMounted(() => {
      handleYearChange()
    })

    onUnmounted(() => {
      if (abortController) {
        abortController.abort()
      }
    })

    return {
      selectedYear,
      availableYears,
      currentData,
      loading,
      maxProjectValue,
      isEditMode,
      saving,
      toast,
      dashboardConfig,
      visibleCards,
      chartRows,
      maxValue,
      toggleSidebar,
      handleYearChange,
      enableEditMode,
      cancelEdit,
      saveConfig,
      toggleCardVisibility,
      toggleChartVisibility,
      handleDragStart,
      handleDragOver,
      handleDrop,
      getCardClass,
      getCardLabel,
      getCardDataKey,
      getChartTitle
    }
  }
})
</script>

<style scoped>
.statistics-page {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.menu-toggle {
  cursor: pointer;
  padding: 10px;
  border-radius: 6px;
  transition: background 0.3s;
}

.menu-toggle:hover {
  background: #e8e8e8;
}

.year-selector {
  display: flex;
  align-items: center;
  gap: 10px;
}

.year-label {
  font-weight: 600;
  color: #333;
}

.year-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
}

.edit-controls {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-edit {
  background: #1976d2;
  color: white;
}

.btn-edit:hover {
  background: #1565c0;
}

.btn-save {
  background: #4caf50;
  color: white;
}

.btn-save:hover:not(:disabled) {
  background: #45a049;
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-cancel {
  background: #f5f5f5;
  color: #666;
  border: 1px solid #ddd;
}

.btn-cancel:hover {
  background: #e0e0e0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 16px;
}

.user-name {
  font-weight: 600;
  color: #333;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.cards-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.cards-section.edit-mode {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
  position: relative;
  min-height: 120px;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-card.edit-mode {
  cursor: move;
  border: 2px dashed #1976d2;
}

.stat-card.edit-mode:hover {
  border-color: #1565c0;
}

.card-actions {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 5px;
}

.action-btn {
  padding: 4px 8px;
  font-size: 12px;
  background: #1976d2;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  transition: background 0.2s;
}

.action-btn:hover {
  background: #1565c0;
}

.card-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
}

.card-value {
  font-size: 32px;
  font-weight: bold;
  color: #333;
}

.card-near-expiry {
  border-left: 4px solid #ff9800;
}

.card-overdue {
  border-left: 4px solid #dc2626;
}

.card-completed {
  border-left: 4px solid #1976d2;
}

.card-regular {
  border-left: 4px solid #059669;
}

.card-temporary {
  border-left: 4px solid #d97706;
}

.card-sporadic {
  border-left: 4px solid #722ed1;
}

.charts-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.charts-section.edit-mode {
  gap: 25px;
}

.chart-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.chart-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

.chart-container.edit-mode {
  border: 2px dashed #1976d2;
  cursor: move;
}

.chart-container.edit-mode:hover {
  border-color: #1565c0;
}

.chart-container.hidden {
  display: none;
}

.chart-actions {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 5px;
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 15px;
}

.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.horizontal-bar-chart {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.bar-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.bar-label {
  min-width: 100px;
  font-size: 14px;
  color: #666;
}

.bar-wrapper {
  flex: 1;
  height: 24px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.bar {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.5s ease;
}

.bar-value {
  margin-left: 10px;
  font-weight: 600;
  color: #333;
}

.vertical-bar-chart {
  display: flex;
  align-items: flex-end;
  height: 300px;
  gap: 15px;
}

.vertical-bars {
  display: flex;
  align-items: flex-end;
  height: 100%;
  gap: 10px;
}

.vertical-bar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}

.vertical-bar-wrapper {
  width: 60px;
  height: 100%;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: center;
}

.vertical-bar {
  width: 100%;
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  transition: height 0.5s ease;
}

.vertical-bar-value {
  margin-bottom: 5px;
  font-weight: 600;
  color: #333;
}

.vertical-bar-label {
  font-size: 12px;
  color: #666;
  text-align: center;
}

.pie-chart {
  display: flex;
  align-items: center;
  gap: 20px;
}

.pie-chart-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.pie-svg {
  width: 200px;
  height: 200px;
}

.pie-legend {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-color {
  width: 20px;
  height: 20px;
  border-radius: 4px;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
