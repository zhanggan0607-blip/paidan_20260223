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

    <div class="content">
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
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue'

interface WorkOrderItem {
  name: string
  value: number
}

interface YearData {
  nearExpiry: number
  overdue: number
  completed: number
  regularInspection: number
  temporaryRepair: number
  sporadicLabor: number
  workOrderByPerson: WorkOrderItem[]
  inspectionByPerson: WorkOrderItem[]
  repairByPerson: WorkOrderItem[]
  laborByPerson: WorkOrderItem[]
  onTimeRate: number
  topProjects: WorkOrderItem[]
}

interface MockData {
  [key: number]: YearData
}

export default defineComponent({
  name: 'StatisticsPage',
  setup() {
    const selectedYear = ref<number>(2026)
    const availableYears = [2024, 2025, 2026, 2027, 2028]

    const mockData: MockData = {
      2026: {
        nearExpiry: 12,
        overdue: 3,
        completed: 221,
        regularInspection: 2223,
        temporaryRepair: 1123,
        sporadicLabor: 193,
        workOrderByPerson: [
          { name: '晋海龙', value: 45 },
          { name: '王五', value: 38 },
          { name: '李四', value: 52 },
          { name: '张三', value: 41 },
          { name: '刘启智', value: 35 }
        ],
        inspectionByPerson: [
          { name: '晋海龙', value: 520 },
          { name: '王五', value: 480 },
          { name: '李四', value: 550 },
          { name: '张三', value: 490 },
          { name: '刘启智', value: 183 }
        ],
        repairByPerson: [
          { name: '晋海龙', value: 280 },
          { name: '王五', value: 240 },
          { name: '李四', value: 300 },
          { name: '张三', value: 250 },
          { name: '刘启智', value: 53 }
        ],
        laborByPerson: [
          { name: '晋海龙', value: 50 },
          { name: '王五', value: 45 },
          { name: '李四', value: 48 },
          { name: '张三', value: 40 },
          { name: '刘启智', value: 10 }
        ],
        onTimeRate: 0.68,
        topProjects: [
          { name: '项目A', value: 85 },
          { name: '项目B', value: 72 },
          { name: '项目C', value: 65 },
          { name: '项目D', value: 58 },
          { name: '项目E', value: 45 }
        ]
      },
      2025: {
        nearExpiry: 8,
        overdue: 2,
        completed: 198,
        regularInspection: 1950,
        temporaryRepair: 980,
        sporadicLabor: 165,
        workOrderByPerson: [
          { name: '晋海龙', value: 40 },
          { name: '王五', value: 35 },
          { name: '李四', value: 45 },
          { name: '张三', value: 38 },
          { name: '刘启智', value: 30 }
        ],
        inspectionByPerson: [
          { name: '晋海龙', value: 450 },
          { name: '王五', value: 420 },
          { name: '李四', value: 480 },
          { name: '张三', value: 430 },
          { name: '刘启智', value: 170 }
        ],
        repairByPerson: [
          { name: '晋海龙', value: 250 },
          { name: '王五', value: 210 },
          { name: '李四', value: 270 },
          { name: '张三', value: 220 },
          { name: '刘启智', value: 30 }
        ],
        laborByPerson: [
          { name: '晋海龙', value: 45 },
          { name: '王五', value: 40 },
          { name: '李四', value: 42 },
          { name: '张三', value: 35 },
          { name: '刘启智', value: 8 }
        ],
        onTimeRate: 0.72,
        topProjects: [
          { name: '项目A', value: 75 },
          { name: '项目B', value: 65 },
          { name: '项目C', value: 58 },
          { name: '项目D', value: 52 },
          { name: '项目E', value: 40 }
        ]
      },
      2024: {
        nearExpiry: 5,
        overdue: 1,
        completed: 175,
        regularInspection: 1680,
        temporaryRepair: 850,
        sporadicLabor: 140,
        workOrderByPerson: [
          { name: '晋海龙', value: 35 },
          { name: '王五', value: 30 },
          { name: '李四', value: 40 },
          { name: '张三', value: 32 },
          { name: '刘启智', value: 25 }
        ],
        inspectionByPerson: [
          { name: '晋海龙', value: 380 },
          { name: '王五', value: 350 },
          { name: '李四', value: 410 },
          { name: '张三', value: 370 },
          { name: '刘启智', value: 170 }
        ],
        repairByPerson: [
          { name: '晋海龙', value: 220 },
          { name: '王五', value: 180 },
          { name: '李四', value: 240 },
          { name: '张三', value: 190 },
          { name: '刘启智', value: 20 }
        ],
        laborByPerson: [
          { name: '晋海龙', value: 38 },
          { name: '王五', value: 35 },
          { name: '李四', value: 38 },
          { name: '张三', value: 30 },
          { name: '刘启智', value: 6 }
        ],
        onTimeRate: 0.75,
        topProjects: [
          { name: '项目A', value: 65 },
          { name: '项目B', value: 58 },
          { name: '项目C', value: 52 },
          { name: '项目D', value: 45 },
          { name: '项目E', value: 35 }
        ]
      }
    }

    const currentData = computed(() => {
      return mockData[selectedYear.value] || mockData[2026]
    })

    const maxValue = computed(() => {
      const allValues = [
        ...currentData.value.workOrderByPerson.map((item: WorkOrderItem) => item.value),
        ...currentData.value.inspectionByPerson.map((item: WorkOrderItem) => item.value),
        ...currentData.value.repairByPerson.map((item: WorkOrderItem) => item.value),
        ...currentData.value.laborByPerson.map((item: WorkOrderItem) => item.value)
      ]
      return Math.max(...allValues)
    })

    const maxProjectValue = computed(() => {
      return Math.max(...currentData.value.topProjects.map((item: WorkOrderItem) => item.value))
    })

    const handleYearChange = () => {
      console.log('Year changed to:', selectedYear.value)
    }

    const toggleSidebar = () => {
      console.log('Toggle sidebar')
    }

    return {
      selectedYear,
      availableYears,
      currentData,
      maxValue,
      maxProjectValue,
      handleYearChange,
      toggleSidebar
    }
  }
})
</script>

<style scoped>
.statistics-page {
  background: #fff;
  min-height: 100vh;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: #F5F7FA;
  border-bottom: 1px solid #e0e0e0;
}

.menu-toggle {
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.menu-toggle:hover {
  background: rgba(0, 0, 0, 0.05);
}

.year-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

.year-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.year-select {
  padding: 6px 12px;
  border: 1px solid #d0d7de;
  border-radius: 4px;
  font-size: 14px;
  color: #333;
  background: #fff;
  cursor: pointer;
  outline: none;
}

.year-select:focus {
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 12px;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1976d2 0%, #42a5f5 100%);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-name {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.content {
  padding: 20px;
}

.cards-section {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
  margin-bottom: 24px;
  width: 100%;
}

.stat-card {
  padding: 20px;
  border-radius: 8px;
  background: #fff;
  border: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.card-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.card-value {
  font-size: 28px;
  font-weight: 700;
}

.card-near-expiry .card-value {
  color: #1976d2;
}

.card-overdue .card-value {
  color: #d32f2f;
}

.card-completed .card-value,
.card-regular .card-value,
.card-temporary .card-value,
.card-sporadic .card-value {
  color: #424242;
}

.charts-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chart-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.chart-container {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px 0;
}

.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.horizontal-bar-chart .bar-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.horizontal-bar-chart .bar-label {
  min-width: 80px;
  font-size: 14px;
  color: #666;
  text-align: right;
}

.horizontal-bar-chart .bar-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  height: 32px;
  background: #f5f5f5;
  border-radius: 4px;
  padding: 0 8px;
}

.horizontal-bar-chart .bar {
  height: 24px;
  background: linear-gradient(90deg, #1976d2 0%, #42a5f5 100%);
  border-radius: 4px;
  transition: width 0.3s ease;
  min-width: 0;
}

.horizontal-bar-chart .bar-value {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.pie-chart {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.pie-chart-container {
  width: 200px;
  height: 200px;
  position: relative;
}

.pie-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
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
  font-size: 14px;
  color: #666;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.vertical-bar-chart {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  height: 250px;
  padding: 20px 0;
}

.vertical-bars {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  width: 100%;
  height: 250px;
  padding: 20px 0;
}

.vertical-bar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.vertical-bar-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 200px;
  width: 100%;
  position: relative;
}

.vertical-bar {
  width: 40px;
  background: linear-gradient(180deg, #1976d2 0%, #42a5f5 100%);
  border-radius: 4px 4px 0 0;
  transition: height 0.3s ease;
  min-height: 0;
}

.vertical-bar-value {
  font-size: 12px;
  font-weight: 600;
  color: #333;
  margin-top: 4px;
}

.vertical-bar-label {
  font-size: 12px;
  color: #666;
  text-align: center;
  margin-top: 4px;
}

@media (max-width: 1400px) {
  .cards-section {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 1024px) {
  .cards-section {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .chart-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .cards-section {
    grid-template-columns: 1fr;
  }
  
  .top-bar {
    flex-direction: column;
    gap: 12px;
  }
}
</style>
