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
      <div class="top-cards-section">
        <div class="mini-card mini-card-warning">
          <div class="mini-card-value">{{ overviewData.nearDueCount }}</div>
          <div class="mini-card-label">临期工单</div>
        </div>
        <div class="mini-card mini-card-danger">
          <div class="mini-card-value">{{ overviewData.overdueCount }}</div>
          <div class="mini-card-label">超期工单</div>
        </div>
        <div class="mini-card mini-card-success">
          <div class="mini-card-value">{{ overviewData.yearCompletedCount }}</div>
          <div class="mini-card-label">本年完成</div>
        </div>
        <div class="mini-card mini-card-info">
          <div class="mini-card-value">{{ overviewData.regularInspectionCount }}</div>
          <div class="mini-card-label">定期巡检单</div>
        </div>
        <div class="mini-card mini-card-purple">
          <div class="mini-card-value">{{ overviewData.temporaryRepairCount }}</div>
          <div class="mini-card-label">临时维修单</div>
        </div>
        <div class="mini-card mini-card-cyan">
          <div class="mini-card-value">{{ overviewData.spotWorkCount }}</div>
          <div class="mini-card-label">零星用工单</div>
        </div>
      </div>

      <div class="cards-section">
        <div class="stat-card card-total employee-chart-card">
          <div class="employee-chart-container">
            <div class="chart-caption">本年度工单数量（{{ selectedYear }}）</div>
            <div class="horizontal-bar-chart">
              <div class="chart-y-axis">
                <div v-for="tick in yAxisTicks" :key="tick" class="y-axis-tick">{{ tick }}</div>
              </div>
              <div class="chart-content">
                <div class="chart-grid">
                  <div v-for="tick in yAxisTicks" :key="'grid-' + tick" class="grid-line"></div>
                </div>
                <div class="horizontal-bars">
                  <div v-for="(employee, index) in employeeStats.employees" :key="index" class="horizontal-bar-item">
                    <div class="bar-label">{{ employee.name }}</div>
                    <div class="bar-track">
                      <div class="bar-fill" :style="{ width: getEmployeeBarWidth(employee.count) + '%' }">
                        <span class="bar-value">{{ employee.count }}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="employee-no-data" v-if="employeeStats.employees.length === 0">
                  暂无数据
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="stat-card card-inspection inspection-chart-card">
          <div class="employee-chart-container">
            <div class="chart-caption">定期巡检单完成数量（{{ selectedYear }}）</div>
            <div class="horizontal-bar-chart">
              <div class="chart-y-axis">
                <div v-for="tick in inspectionYAxisTicks" :key="tick" class="y-axis-tick">{{ tick }}</div>
              </div>
              <div class="chart-content">
                <div class="chart-grid">
                  <div v-for="tick in inspectionYAxisTicks" :key="'grid-' + tick" class="grid-line"></div>
                </div>
                <div class="horizontal-bars">
                  <div v-for="(item, index) in inspectionStats.employees" :key="index" class="horizontal-bar-item">
                    <div class="bar-label">{{ item.name }}</div>
                    <div class="bar-track">
                      <div class="bar-fill" :style="{ width: getInspectionBarWidth(item.count) + '%' }">
                        <span class="bar-value">{{ item.count }}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="employee-no-data" v-if="inspectionStats.employees.length === 0">
                  暂无数据
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="stat-card card-repair repair-chart-card">
          <div class="employee-chart-container">
            <div class="chart-caption">临时维修单完成数量（{{ selectedYear }}）</div>
            <div class="horizontal-bar-chart">
              <div class="chart-y-axis">
                <div v-for="tick in repairYAxisTicks" :key="tick" class="y-axis-tick">{{ tick }}</div>
              </div>
              <div class="chart-content">
                <div class="chart-grid">
                  <div v-for="tick in repairYAxisTicks" :key="'grid-' + tick" class="grid-line"></div>
                </div>
                <div class="horizontal-bars">
                  <div v-for="(item, index) in repairStats.employees" :key="index" class="horizontal-bar-item">
                    <div class="bar-label">{{ item.name }}</div>
                    <div class="bar-track">
                      <div class="bar-fill" :style="{ width: getRepairBarWidth(item.count) + '%' }">
                        <span class="bar-value">{{ item.count }}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="employee-no-data" v-if="repairStats.employees.length === 0">
                  暂无数据
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="stat-card card-labor spotwork-chart-card">
          <div class="employee-chart-container">
            <div class="chart-caption">零星用工单完成数量（{{ selectedYear }}）</div>
            <div class="horizontal-bar-chart">
              <div class="chart-y-axis">
                <div v-for="tick in spotworkYAxisTicks" :key="tick" class="y-axis-tick">{{ tick }}</div>
              </div>
              <div class="chart-content">
                <div class="chart-grid">
                  <div v-for="tick in spotworkYAxisTicks" :key="'grid-' + tick" class="grid-line"></div>
                </div>
                <div class="horizontal-bars">
                  <div v-for="(item, index) in spotworkStats.employees" :key="index" class="horizontal-bar-item">
                    <div class="bar-label">{{ item.name }}</div>
                    <div class="bar-track">
                      <div class="bar-fill" :style="{ width: getSpotworkBarWidth(item.count) + '%' }">
                        <span class="bar-value">{{ item.count }}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="employee-no-data" v-if="spotworkStats.employees.length === 0">
                  暂无数据
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="cards-section">
        <div class="stat-card card-total employee-chart-card">
          <div class="employee-chart-container">
            <div class="chart-caption">准时完成情况分布（{{ selectedYear }}）</div>
            <div class="pie-chart-wrapper">
              <div class="pie-chart-container">
                <svg class="pie-svg" viewBox="0 0 100 100">
                  <circle cx="50" cy="50" r="40" fill="none" stroke="#fac858" stroke-width="20" 
                    :stroke-dasharray="pieDashArray" stroke-dashoffset="0" transform="rotate(-90 50 50)" />
                  <circle cx="50" cy="50" r="40" fill="none" stroke="#5470c6" stroke-width="20" 
                    :stroke-dasharray="pieDashArray" :stroke-dashoffset="pieDashOffset" transform="rotate(-90 50 50)" />
                </svg>
                <div class="pie-center">
                  <div class="pie-percentage">{{ Math.round(completionRate.onTimeRate * 100) }}%</div>
                  <div class="pie-label">准时率</div>
                </div>
              </div>
              <div class="pie-legend">
                <div class="legend-item">
                  <div class="legend-color legend-color-ontime"></div>
                  <span>准时完成: {{ completionRate.onTimeCount }}单</span>
                </div>
                <div class="legend-item">
                  <div class="legend-color legend-color-delayed"></div>
                  <span>延期完成: {{ completionRate.delayedCount }}单</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="stat-card card-inspection inspection-chart-card">
          <div class="employee-chart-container">
            <div class="chart-caption">临时维修单前五（{{ selectedYear }}）</div>
            <div class="horizontal-bar-chart">
              <div class="chart-y-axis">
                <div v-for="tick in topRepairYAxisTicks" :key="tick" class="y-axis-tick">{{ tick }}</div>
              </div>
              <div class="chart-content">
                <div class="chart-grid">
                  <div v-for="tick in topRepairYAxisTicks" :key="'grid-' + tick" class="grid-line"></div>
                </div>
                <div class="horizontal-bars">
                  <div v-for="(item, index) in topRepairs" :key="index" class="horizontal-bar-item">
                    <div class="bar-label">{{ truncateName(item.name, 6) }}</div>
                    <div class="bar-track">
                      <div class="bar-fill" :style="{ width: getTopRepairBarWidth(item.value) + '%' }">
                        <span class="bar-value">{{ item.value }}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="employee-no-data" v-if="topRepairs.length === 0">
                  暂无数据
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
import { defineComponent, ref, onMounted, onUnmounted, computed, inject } from 'vue'
import { statisticsService, StatisticsOverview, CompletionRate, TopProject, EmployeeStats } from '@/services/statistics'

export default defineComponent({
  name: 'StatisticsPage',
  setup() {
    const selectedYear = ref<number>(new Date().getFullYear())
    const availableYears = [2024, 2025, 2026, 2027, 2028]
    const overviewData = ref<StatisticsOverview>({
      year: selectedYear.value,
      totalWorkOrders: 0,
      regularInspectionCount: 0,
      temporaryRepairCount: 0,
      spotWorkCount: 0,
      nearDueCount: 0,
      overdueCount: 0,
      yearCompletedCount: 0
    })
    const completionRate = ref<CompletionRate>({
      year: selectedYear.value,
      onTimeRate: 0,
      onTimeCount: 0,
      delayedCount: 0,
      totalCount: 0
    })
    const topProjects = ref<TopProject[]>([])
    const topRepairs = ref<TopProject[]>([])
    const employeeStats = ref<EmployeeStats>({
      year: selectedYear.value,
      employees: [],
      total: 0
    })
    const inspectionStats = ref<EmployeeStats>({
      year: selectedYear.value,
      employees: [],
      total: 0
    })
    const repairStats = ref<EmployeeStats>({
      year: selectedYear.value,
      employees: [],
      total: 0
    })
    const spotworkStats = ref<EmployeeStats>({
      year: selectedYear.value,
      employees: [],
      total: 0
    })
    const loading = ref<boolean>(false)
    const isFullscreen = ref<boolean>(false)
    
    const setFullscreenMode = inject<(value: boolean) => void>('setFullscreenMode')

    const maxProjectValue = computed(() => {
      if (topRepairs.value.length === 0) return 1
      return Math.max(...topRepairs.value.map(p => p.value), 1)
    })

    const maxEmployeeValue = computed(() => {
      if (employeeStats.value.employees.length === 0) return 10
      return Math.max(...employeeStats.value.employees.map(e => e.count), 10)
    })

    const maxInspectionValue = computed(() => {
      if (inspectionStats.value.employees.length === 0) return 10
      return Math.max(...inspectionStats.value.employees.map(e => e.count), 10)
    })

    const maxRepairValue = computed(() => {
      if (repairStats.value.employees.length === 0) return 10
      return Math.max(...repairStats.value.employees.map(e => e.count), 10)
    })

    const maxSpotworkValue = computed(() => {
      if (spotworkStats.value.employees.length === 0) return 10
      return Math.max(...spotworkStats.value.employees.map(e => e.count), 10)
    })

    const maxTopRepairValue = computed(() => {
      if (topRepairs.value.length === 0) return 10
      return Math.max(...topRepairs.value.map(e => e.value), 10)
    })

    const yAxisTicks = computed(() => {
      const maxValue = maxEmployeeValue.value
      const tickCount = Math.ceil(maxValue / 10)
      const ticks: number[] = []
      for (let i = 0; i <= tickCount; i++) {
        ticks.push(i * 10)
      }
      return ticks
    })

    const inspectionYAxisTicks = computed(() => {
      const maxValue = maxInspectionValue.value
      const tickCount = Math.ceil(maxValue / 10)
      const ticks: number[] = []
      for (let i = 0; i <= tickCount; i++) {
        ticks.push(i * 10)
      }
      return ticks
    })

    const repairYAxisTicks = computed(() => {
      const maxValue = maxRepairValue.value
      const tickCount = Math.ceil(maxValue / 10)
      const ticks: number[] = []
      for (let i = 0; i <= tickCount; i++) {
        ticks.push(i * 10)
      }
      return ticks
    })

    const spotworkYAxisTicks = computed(() => {
      const maxValue = maxSpotworkValue.value
      const tickCount = Math.ceil(maxValue / 10)
      const ticks: number[] = []
      for (let i = 0; i <= tickCount; i++) {
        ticks.push(i * 10)
      }
      return ticks
    })

    const topRepairYAxisTicks = computed(() => {
      const maxValue = maxTopRepairValue.value
      const tickCount = Math.ceil(maxValue / 10)
      const ticks: number[] = []
      for (let i = 0; i <= tickCount; i++) {
        ticks.push(i * 10)
      }
      return ticks
    })

    const getBarHeight = (value: number) => {
      if (maxProjectValue.value === 0) return 0
      return (value / maxProjectValue.value) * 100
    }

    const getEmployeeBarWidth = (value: number) => {
      const maxValue = Math.max(...yAxisTicks.value)
      if (maxValue === 0) return 0
      return (value / maxValue) * 100
    }

    const getInspectionBarWidth = (value: number) => {
      const maxValue = Math.max(...inspectionYAxisTicks.value)
      if (maxValue === 0) return 0
      return (value / maxValue) * 100
    }

    const getRepairBarWidth = (value: number) => {
      const maxValue = Math.max(...repairYAxisTicks.value)
      if (maxValue === 0) return 0
      return (value / maxValue) * 100
    }

    const getSpotworkBarWidth = (value: number) => {
      const maxValue = Math.max(...spotworkYAxisTicks.value)
      if (maxValue === 0) return 0
      return (value / maxValue) * 100
    }

    const getTopRepairBarWidth = (value: number) => {
      const maxValue = Math.max(...topRepairYAxisTicks.value)
      if (maxValue === 0) return 0
      return (value / maxValue) * 100
    }

    const pieDashArray = computed(() => {
      const circumference = 2 * Math.PI * 40
      return `${circumference} ${circumference}`
    })

    const pieDashOffset = computed(() => {
      const circumference = 2 * Math.PI * 40
      const onTimeRatio = completionRate.value.onTimeRate
      return circumference * (1 - onTimeRatio)
    })

    const truncateName = (name: string, maxLen: number) => {
      if (!name) return ''
      if (name.length <= maxLen) return name
      return name.substring(0, maxLen) + '...'
    }

    const toggleFullscreen = () => {
      isFullscreen.value = !isFullscreen.value
      if (isFullscreen.value) {
        document.documentElement.requestFullscreen()
        if (setFullscreenMode) {
          setFullscreenMode(true)
        }
      } else {
        document.exitFullscreen()
        if (setFullscreenMode) {
          setFullscreenMode(false)
        }
      }
    }

    const handleYearChange = async () => {
      loading.value = true
      try {
        const [overview, rate, projects, topRepairsData, employees, inspections, repairs, spotworks] = await Promise.all([
          statisticsService.getStatisticsOverview(selectedYear.value),
          statisticsService.getCompletionRate(selectedYear.value),
          statisticsService.getTopProjects(selectedYear.value, 5),
          statisticsService.getTopRepairs(selectedYear.value, 5),
          statisticsService.getEmployeeStats(selectedYear.value),
          statisticsService.getInspectionStats(selectedYear.value),
          statisticsService.getRepairStats(selectedYear.value),
          statisticsService.getSpotworkStats(selectedYear.value)
        ])
        
        overviewData.value = overview
        completionRate.value = rate
        topProjects.value = projects
        topRepairs.value = topRepairsData
        employeeStats.value = employees
        inspectionStats.value = inspections
        repairStats.value = repairs
        spotworkStats.value = spotworks
      } catch (error) {
        console.error('获取统计数据失败:', error)
      } finally {
        loading.value = false
      }
    }

    const handleFullscreenChange = () => {
      if (!document.fullscreenElement) {
        isFullscreen.value = false
        if (setFullscreenMode) {
          setFullscreenMode(false)
        }
      }
    }

    onMounted(() => {
      handleYearChange()
      document.addEventListener('fullscreenchange', handleFullscreenChange)
    })

    onUnmounted(() => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange)
    })

    return {
      selectedYear,
      availableYears,
      overviewData,
      completionRate,
      topProjects,
      topRepairs,
      employeeStats,
      inspectionStats,
      repairStats,
      spotworkStats,
      loading,
      isFullscreen,
      maxProjectValue,
      maxEmployeeValue,
      yAxisTicks,
      inspectionYAxisTicks,
      repairYAxisTicks,
      spotworkYAxisTicks,
      topRepairYAxisTicks,
      getBarHeight,
      getEmployeeBarWidth,
      getInspectionBarWidth,
      getRepairBarWidth,
      getSpotworkBarWidth,
      getTopRepairBarWidth,
      pieDashArray,
      pieDashOffset,
      truncateName,
      toggleFullscreen,
      handleYearChange
    }
  }
})
</script>

<style scoped>
.statistics-page {
  padding: 20px;
  background: #f5f7fa;
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
}

.top-cards-section {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
}

.mini-card {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  text-align: center;
  transition: transform 0.2s, box-shadow 0.2s;
}

.mini-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.mini-card-value {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 4px;
}

.mini-card-label {
  font-size: 12px;
  color: #666;
}

.mini-card-warning {
  border-left: 4px solid #FF9800;
}

.mini-card-warning .mini-card-value {
  color: #FF9800;
}

.mini-card-danger {
  border-left: 4px solid #F44336;
}

.mini-card-danger .mini-card-value {
  color: #F44336;
}

.mini-card-success {
  border-left: 4px solid #4CAF50;
}

.mini-card-success .mini-card-value {
  color: #4CAF50;
}

.mini-card-info {
  border-left: 4px solid #2196F3;
}

.mini-card-info .mini-card-value {
  color: #2196F3;
}

.mini-card-purple {
  border-left: 4px solid #9C27B0;
}

.mini-card-purple .mini-card-value {
  color: #9C27B0;
}

.mini-card-cyan {
  border-left: 4px solid #00BCD4;
}

.mini-card-cyan .mini-card-value {
  color: #00BCD4;
}

.cards-section {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-auto-rows: 1fr;
  gap: 20px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-total .card-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.card-inspection .card-icon {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  color: white;
}

.card-repair .card-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.card-labor .card-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.card-content {
  flex: 1;
}

.card-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.card-value {
  font-size: 36px;
  font-weight: 700;
  color: #333;
  line-height: 1;
}

.employee-chart-card,
.inspection-chart-card,
.repair-chart-card,
.spotwork-chart-card {
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
  align-items: stretch;
  height: 100%;
}

.employee-chart-container,
.inspection-chart-container {
  width: 100%;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chart-caption {
  font-size: 1.1rem;
  font-weight: 600;
  color: #0a1a2f;
  letter-spacing: -0.02em;
  margin-bottom: 0.5rem;
  text-align: center;
}

.horizontal-bar-chart {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 110px;
}

.chart-y-axis {
  display: flex;
  justify-content: space-between;
  padding: 0 60px 0 0;
  margin-bottom: 4px;
}

.y-axis-tick {
  font-size: 9px;
  color: #999;
  text-align: center;
  flex: 1;
}

.chart-content {
  flex: 1;
  position: relative;
}

.chart-grid {
  position: absolute;
  top: 0;
  left: 60px;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: space-between;
  pointer-events: none;
}

.grid-line {
  flex: 1;
  border-left: 1px dashed #e8e8e8;
}

.horizontal-bars {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.horizontal-bar-item {
  display: flex;
  align-items: center;
  height: 20px;
}

.bar-label {
  width: 60px;
  font-size: 11px;
  color: #333;
  text-align: right;
  padding-right: 8px;
  flex-shrink: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bar-track {
  flex: 1;
  height: 14px;
  background: #f0f0f0;
  border-radius: 3px;
  overflow: hidden;
  position: relative;
}

.bar-fill {
  height: 100%;
  background: #5470c6;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 6px;
  min-width: 24px;
  transition: width 0.3s ease;
}

.bar-fill-green {
  background: #91cc75;
}

.bar-fill-red {
  background: #ee6666;
}

.bar-value {
  font-size: 10px;
  font-weight: 600;
  color: white;
}

.pie-chart-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  min-height: 110px;
}

.pie-chart-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pie-svg {
  width: 100px;
  height: 100px;
}

.pie-center {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.pie-percentage {
  font-size: 18px;
  font-weight: 700;
  color: #333;
}

.pie-label {
  font-size: 10px;
  color: #666;
  margin-top: 2px;
}

.pie-legend {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: #333;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

.legend-color-ontime {
  background: #5470c6;
}

.legend-color-delayed {
  background: #fac858;
}

.employee-no-data {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #999;
  font-size: 14px;
}

.chart-meta-info {
  margin-top: 0.5rem;
  font-size: 0.7rem;
  color: #7b8ba3;
  border-top: 1px dashed #d0ddeb;
  padding-top: 0.5rem;
  text-align: right;
}

.chartjs-container {
  flex: 1;
  min-height: 140px;
  position: relative;
}

.chart-container {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  min-height: 400px;
  display: flex;
  flex-direction: column;
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 24px;
}

.pie-chart {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 48px;
  flex: 1;
}

.pie-chart-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pie-svg {
  width: 200px;
  height: 200px;
}

.pie-center {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.pie-percentage {
  font-size: 32px;
  font-weight: 700;
  color: #333;
}

.pie-label {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

.pie-legend {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #666;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.legend-color-ontime {
  background: #4CAF50;
}

.legend-color-delayed {
  background: #FF6B6B;
}

.vertical-bar-chart {
  flex: 1;
  display: flex;
  align-items: flex-end;
}

.vertical-bars {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  width: 100%;
  height: 280px;
  padding: 0 20px;
}

.vertical-bar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  max-width: 80px;
}

.vertical-bar-wrapper {
  width: 100%;
  height: 240px;
  background: #f0f0f0;
  border-radius: 8px 8px 0 0;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  overflow: hidden;
}

.vertical-bar {
  width: 100%;
  background: linear-gradient(180deg, #4CAF50 0%, #45a049 100%);
  border-radius: 8px 8px 0 0;
  transition: height 0.3s ease;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 8px;
}

.vertical-bar-value {
  font-weight: 600;
  font-size: 16px;
  color: white;
}

.vertical-bar-label {
  margin-top: 12px;
  font-size: 12px;
  color: #666;
  text-align: center;
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

@media (max-width: 1200px) {
  .top-cards-section {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .top-cards-section {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .cards-section {
    grid-template-columns: 1fr;
  }
  
  .top-bar {
    flex-direction: column;
    gap: 12px;
  }
}

:fullscreen .statistics-page {
  min-height: 100vh;
  height: 100vh;
  width: 100vw;
  padding: 12px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

:fullscreen .top-bar {
  flex-shrink: 0;
  padding: 10px 16px;
  margin-bottom: 8px;
}

:fullscreen .content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 0;
  overflow: hidden;
}

:fullscreen .top-cards-section {
  flex-shrink: 0;
  gap: 8px;
}

:fullscreen .mini-card {
  padding: 8px 10px;
}

:fullscreen .mini-card-value {
  font-size: 22px;
}

:fullscreen .mini-card-label {
  font-size: 10px;
}

:fullscreen .cards-section {
  flex: 1;
  min-height: 0;
  gap: 8px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: repeat(2, 1fr);
  overflow: hidden;
}

:fullscreen .stat-card {
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  overflow: hidden;
}

:fullscreen .employee-chart-card,
:fullscreen .inspection-chart-card,
:fullscreen .repair-chart-card,
:fullscreen .spotwork-chart-card {
  height: 100%;
  min-height: 0;
}

:fullscreen .employee-chart-container,
:fullscreen .inspection-chart-container {
  padding: 8px;
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

:fullscreen .chart-caption {
  font-size: 0.9rem;
  margin-bottom: 4px;
  flex-shrink: 0;
}

:fullscreen .horizontal-bar-chart {
  min-height: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

:fullscreen .chart-y-axis {
  flex-shrink: 0;
  margin-bottom: 2px;
}

:fullscreen .chart-content {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

:fullscreen .chart-grid {
  display: none;
}

:fullscreen .horizontal-bars {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-evenly;
}

:fullscreen .horizontal-bar-item {
  height: auto;
  flex: 1 1 auto;
  min-height: 18px;
  max-height: 24px;
  display: flex;
  align-items: center;
}

:fullscreen .bar-label {
  font-size: 11px;
  width: 60px;
}

:fullscreen .bar-track {
  height: 14px;
}

:fullscreen .bar-value {
  font-size: 10px;
}

:fullscreen .y-axis-tick {
  font-size: 9px;
}

:fullscreen .pie-chart-wrapper {
  min-height: 0;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

:fullscreen .pie-chart-container {
  position: relative;
}

:fullscreen .pie-svg {
  width: 100px;
  height: 100px;
}

:fullscreen .pie-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

:fullscreen .pie-percentage {
  font-size: 18px;
}

:fullscreen .pie-label {
  font-size: 9px;
}

:fullscreen .pie-legend {
  gap: 6px;
}

:fullscreen .legend-item {
  font-size: 11px;
  gap: 6px;
}

:fullscreen .legend-color {
  width: 12px;
  height: 12px;
}

:fullscreen .employee-no-data {
  font-size: 12px;
}
</style>
