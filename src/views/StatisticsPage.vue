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
      <div class="user-info">
        <div class="user-avatar">MO</div>
        <span class="user-name">momo.zxy</span>
      </div>
    </div>

    <div class="content" v-if="!loading">
      <div class="cards-section">
        <div class="stat-card card-near-expiry">
          <div class="card-label">临期工单</div>
          <div class="card-value">{{ currentData.nearExpiry }}</div>
        </div>
        <div class="stat-card card-overdue">
          <div class="card-label">超期工单</div>
          <div class="card-value">{{ currentData.overdue }}</div>
        </div>
        <div class="stat-card card-completed">
          <div class="card-label">本年完成</div>
          <div class="card-value">{{ currentData.completed }}</div>
        </div>
        <div class="stat-card card-regular">
          <div class="card-label">定期巡检单</div>
          <div class="card-value">{{ currentData.regularInspection }}</div>
        </div>
        <div class="stat-card card-temporary">
          <div class="card-label">临时维修单</div>
          <div class="card-value">{{ currentData.temporaryRepair }}</div>
        </div>
        <div class="stat-card card-sporadic">
          <div class="card-label">零星用工单</div>
          <div class="card-value">{{ currentData.sporadicLabor }}</div>
        </div>
      </div>

      <div class="charts-section">
        <div class="chart-row">
          <div class="chart-container">
            <h3 class="chart-title">本年度工单数量（{{ selectedYear }}）</h3>
            <div class="bar-chart horizontal-bar-chart">
              <div v-for="(item, index) in currentData.workOrderByPerson" :key="index" class="bar-item">
                <div class="bar-label">{{ item.name }}</div>
                <div class="bar-wrapper">
                  <div class="bar" :style="{ width: (item.value / maxValue * 100) + '%' }"></div>
                  <div class="bar-value">{{ item.value }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="chart-row">
          <div class="chart-container">
            <h3 class="chart-title">定期巡检单完成数量（{{ selectedYear }}）</h3>
            <div class="bar-chart horizontal-bar-chart">
              <div v-for="(item, index) in currentData.inspectionByPerson" :key="index" class="bar-item">
                <div class="bar-label">{{ item.name }}</div>
                <div class="bar-wrapper">
                  <div class="bar" :style="{ width: (item.value / maxValue * 100) + '%' }"></div>
                  <div class="bar-value">{{ item.value }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="chart-row">
          <div class="chart-container">
            <h3 class="chart-title">临时维修单完成数量（{{ selectedYear }}）</h3>
            <div class="bar-chart horizontal-bar-chart">
              <div v-for="(item, index) in currentData.repairByPerson" :key="index" class="bar-item">
                <div class="bar-label">{{ item.name }}</div>
                <div class="bar-wrapper">
                  <div class="bar" :style="{ width: (item.value / maxValue * 100) + '%' }"></div>
                  <div class="bar-value">{{ item.value }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="chart-row">
          <div class="chart-container">
            <h3 class="chart-title">零星用工单完成数量（{{ selectedYear }}）</h3>
            <div class="bar-chart horizontal-bar-chart">
              <div v-for="(item, index) in currentData.laborByPerson" :key="index" class="bar-item">
                <div class="bar-label">{{ item.name }}</div>
                <div class="bar-wrapper">
                  <div class="bar" :style="{ width: (item.value / maxValue * 100) + '%' }"></div>
                  <div class="bar-value">{{ item.value }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="chart-row">
          <div class="chart-container">
            <h3 class="chart-title">准时完成情况分布（{{ selectedYear }}）</h3>
            <div class="pie-chart">
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
          </div>
        </div>
        <div class="chart-row">
          <div class="chart-container">
            <h3 class="chart-title">临时维修年度前五（{{ selectedYear }}）</h3>
            <div class="bar-chart vertical-bar-chart">
              <div class="vertical-bars">
                <div v-for="(item, index) in currentData.topProjects" :key="index" class="vertical-bar-item">
                  <div class="vertical-bar-wrapper">
                    <div class="vertical-bar" :style="{ height: (item.value / maxProjectValue * 100) + '%' }"></div>
                    <div class="vertical-bar-value">{{ item.value }}</div>
                  </div>
                  <div class="vertical-bar-label">{{ item.name }}</div>
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
import { defineComponent, ref, onMounted } from 'vue'
import { statisticsService, StatisticsOverview, WorkByPerson, CompletionRate, TopProject } from '@/services/statistics'

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
      regularInspection: 0,
      temporaryRepair: 0,
      sporadicLabor: 0,
      workOrderByPerson: [] as WorkByPerson[],
      inspectionByPerson: [] as WorkByPerson[],
      repairByPerson: [] as WorkByPerson[],
      laborByPerson: [] as WorkByPerson[],
      onTimeRate: 0,
      topProjects: [] as TopProject[]
    })
    const loading = ref<boolean>(false)
    const maxProjectValue = ref<number>(0)

    const toggleSidebar = () => {
    }

    const handleYearChange = async () => {
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
          regularInspection: overview.regularInspectionCount,
          temporaryRepair: overview.temporaryRepairCount,
          sporadicLabor: overview.spotWorkCount,
          workOrderByPerson: workByPerson,
          inspectionByPerson: workByPerson,
          repairByPerson: workByPerson,
          laborByPerson: workByPerson,
          onTimeRate: completionRate.onTimeRate,
          topProjects: topProjects
        }

        maxProjectValue.value = Math.max(...topProjects.map(p => p.value), 0)
      } catch (error) {
        console.error('加载统计数据失败:', error)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      handleYearChange()
    })

    return {
      selectedYear,
      availableYears,
      currentData,
      loading,
      maxProjectValue,
      toggleSidebar,
      handleYearChange
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

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
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