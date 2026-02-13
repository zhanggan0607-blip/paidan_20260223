<template>
  <div class="statistics-page">
    <div class="top-bar">
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
          编辑布局
        </button>
      </div>
      <div class="refresh-controls">
        <button class="btn btn-refresh" @click="handleYearChange">
          刷新
        </button>
        <button class="btn btn-fullscreen" @click="toggleFullscreen">
          {{ isFullscreen ? '退出全屏' : '全屏' }}
        </button>
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
                    stroke="#4CAF50"
                    transform="rotate(-90 50 50)"
                  />
                  <circle cx="50" cy="50" r="40" fill="none" stroke-width="20"
                    :stroke-dasharray="`${(1 - currentData.onTimeRate) * 251.2} ${251.2 - (1 - currentData.onTimeRate) * 251.2}`"
                    stroke="#FF6B6B"
                    transform="rotate(-90 50 50)"
                  />
                </svg>
              </div>
              <div class="pie-legend">
                <div class="legend-item">
                  <div class="legend-color legend-color-delayed"></div>
                  <span>延期完成（{{ Math.round((1 - currentData.onTimeRate) * 100) }}%）</span>
                </div>
                <div class="legend-item">
                  <div class="legend-color legend-color-ontime"></div>
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

    <div class="toast" v-if="toast.visible">
      <div class="toast-content" :class="toast.type">
        {{ toast.message }}
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onUnmounted, computed } from 'vue'
import { statisticsService, StatisticsOverview, WorkByPerson, CompletionRate, TopProject } from '@/services/statistics'
import { userDashboardConfigService, type DashboardConfig } from '@/services/userDashboardConfig'

export default defineComponent({
  name: 'StatisticsPage',
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
    const isFullscreen = ref<boolean>(false)
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
      if (!dashboardConfig.value || !dashboardConfig.value.cards) {
        return []
      }
      return dashboardConfig.value.cards.filter(c => c.visible).sort((a, b) => a.position - b.position)
    })

    const chartRows = computed(() => {
      if (!dashboardConfig.value || !dashboardConfig.value.charts) {
        return []
      }
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

    const toggleFullscreen = () => {
      isFullscreen.value = !isFullscreen.value
      if (isFullscreen.value) {
        document.documentElement.requestFullscreen()
      } else {
        document.exitFullscreen()
      }
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
          dashboardConfig.value = response.data.config || dashboardConfig.value
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
      isFullscreen,
      saving,
      toast,
      dashboardConfig,
      visibleCards,
      chartRows,
      maxValue,
      toggleSidebar,
      toggleFullscreen,
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
  padding: 240px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  min-height: 100vh;
  font-family: 'Inter', '思源黑体', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  box-sizing: border-box;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  margin-bottom: 24px;
}

.year-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

.year-label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.year-select {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  background: white;
  color: #333;
  outline: none;
}

.year-select:focus {
  border-color: #4CAF50;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
}

.edit-controls {
  display: flex;
  gap: 8px;
}

.refresh-controls {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
  color: white;
}

.btn-edit {
  background: #4CAF50;
}

.btn-edit:hover {
  background: #45a049;
}

.btn-save {
  background: #4CAF50;
}

.btn-save:hover:not(:disabled) {
  background: #45a049;
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-cancel {
  background: #e0e0e0;
  color: #666;
}

.btn-cancel:hover {
  background: #d0d0d0;
}

.btn-refresh {
  background: #4CAF50;
}

.btn-refresh:hover {
  background: #45a049;
}

.btn-fullscreen {
  background: #4CAF50;
}

.btn-fullscreen:hover {
  background: #45a049;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 24px;
  flex: 1;
}

.cards-section {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
}

.cards-section.edit-mode {
  grid-template-columns: repeat(6, 1fr);
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 32px 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  min-height: 160px;
  text-align: center;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.stat-card.edit-mode {
  cursor: move;
  border: 2px dashed #4CAF50;
}

.stat-card.edit-mode:hover {
  border-color: #45a049;
}

.card-actions {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  gap: 6px;
}

.action-btn {
  padding: 6px 12px;
  font-size: 12px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.action-btn:hover {
  background: #45a049;
}

.card-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.card-value {
  font-size: 56px;
  font-weight: 700;
  color: #333;
  line-height: 1;
}

.card-near-expiry {
  border-left: 4px solid #FF6B6B;
}

.card-overdue {
  border-left: 4px solid #DC2626;
}

.card-completed {
  border-left: 4px solid #4CAF50;
}

.card-regular {
  border-left: 4px solid #2196F3;
}

.card-temporary {
  border-left: 4px solid #FF9800;
}

.card-sporadic {
  border-left: 4px solid #722ED1;
}

.charts-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
  flex: 1;
}

.charts-section.edit-mode {
  gap: 28px;
}

.chart-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.chart-container {
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  transition: all 0.2s;
  min-height: 400px;
  display: flex;
  flex-direction: column;
}

.chart-container.edit-mode {
  border: 2px dashed #4CAF50;
  cursor: move;
}

.chart-container.edit-mode:hover {
  border-color: #45a049;
}

.chart-container.hidden {
  display: none;
}

.chart-actions {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  gap: 6px;
}

.chart-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 24px;
}

.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 16px;
  flex: 1;
}

.horizontal-bar-chart {
  display: flex;
  flex-direction: column;
  gap: 16px;
  flex: 1;
}

.bar-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.bar-label {
  min-width: 100px;
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.bar-wrapper {
  flex: 1;
  height: 40px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.bar {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50 0%, #45a049 100%);
  transition: width 0.3s ease;
}

.bar-value {
  margin-left: 16px;
  font-weight: 600;
  font-size: 18px;
  color: #333;
  min-width: 60px;
}

.vertical-bar-chart {
  display: flex;
  align-items: flex-end;
  height: 350px;
  gap: 24px;
  flex: 1;
}

.vertical-bars {
  display: flex;
  align-items: flex-end;
  height: 100%;
  gap: 24px;
  flex: 1;
}

.vertical-bar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.vertical-bar-wrapper {
  width: 100%;
  max-width: 100px;
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
  background: linear-gradient(180deg, #4CAF50 0%, #45a049 100%);
  transition: height 0.3s ease;
}

.vertical-bar-value {
  margin-bottom: 12px;
  font-weight: 600;
  font-size: 18px;
  color: #333;
}

.vertical-bar-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  text-align: center;
}

.pie-chart {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 48px;
  flex: 1;
}

.pie-chart-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.pie-svg {
  width: 240px;
  height: 240px;
}

.pie-legend {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.legend-color-delayed {
  background: #FF6B6B;
}

.legend-color-ontime {
  background: #4CAF50;
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
  border: 4px solid #e0e0e0;
  border-top: 4px solid #4CAF50;
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

.toast {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 1000;
}

.toast-content {
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  min-width: 200px;
}

.toast-content.success {
  background: #4CAF50;
  color: white;
}

.toast-content.error {
  background: #DC2626;
  color: white;
}

.toast-content.warning {
  background: #FF9800;
  color: white;
}

.toast-content.info {
  background: #2196F3;
  color: white;
}
</style>
