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
        <div class="mini-card mini-card-warning clickable" @click="openDetailModal('nearDue', '临期工单')">
          <div class="mini-card-value">{{ overviewData.nearDueCount }}</div>
          <div class="mini-card-label">临期工单</div>
        </div>
        <div class="mini-card mini-card-danger clickable" @click="openDetailModal('overdue', '超期工单')">
          <div class="mini-card-value">{{ overviewData.overdueCount }}</div>
          <div class="mini-card-label">超期工单</div>
        </div>
        <div class="mini-card mini-card-success clickable" @click="openDetailModal('yearCompleted', '本年完成')">
          <div class="mini-card-value">{{ overviewData.yearCompletedCount }}</div>
          <div class="mini-card-label">本年完成</div>
        </div>
        <div class="mini-card mini-card-info clickable" @click="openDetailModal('regularInspection', '定期巡检单')">
          <div class="mini-card-value">{{ overviewData.regularInspectionCount }}</div>
          <div class="mini-card-label">定期巡检单</div>
        </div>
        <div class="mini-card mini-card-purple clickable" @click="openDetailModal('temporaryRepair', '临时维修单')">
          <div class="mini-card-value">{{ overviewData.temporaryRepairCount }}</div>
          <div class="mini-card-label">临时维修单</div>
        </div>
        <div class="mini-card mini-card-cyan clickable" @click="openDetailModal('spotWork', '零星用工单')">
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
                  <div v-for="(employee, index) in employeeStats.employees" :key="index" class="horizontal-bar-item clickable-bar" @click="openEmployeeDetail(employee.name)">
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
                  <div v-for="(item, index) in inspectionStats.employees" :key="index" class="horizontal-bar-item clickable-bar" @click="openEmployeeDetail(item.name, 'inspection')">
                    <div class="bar-label">{{ item.name }}</div>
                    <div class="bar-track">
                      <div class="bar-fill bar-fill-green" :style="{ width: getInspectionBarWidth(item.count) + '%' }">
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
                  <div v-for="(item, index) in repairStats.employees" :key="index" class="horizontal-bar-item clickable-bar" @click="openEmployeeDetail(item.name, 'repair')">
                    <div class="bar-label">{{ item.name }}</div>
                    <div class="bar-track">
                      <div class="bar-fill bar-fill-red" :style="{ width: getRepairBarWidth(item.count) + '%' }">
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
                  <div v-for="(item, index) in spotworkStats.employees" :key="index" class="horizontal-bar-item clickable-bar" @click="openEmployeeDetail(item.name, 'spotwork')">
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

        <div class="stat-card card-total employee-chart-card">
          <div class="employee-chart-container">
            <div class="chart-caption">准时完成情况分布（{{ selectedYear }}）</div>
            <div class="pie-chart-wrapper">
              <div class="pie-chart-container clickable" @click="openDetailModal('onTime', '准时完成')">
                <svg class="pie-svg" viewBox="0 0 100 100">
                  <circle cx="50" cy="50" r="40" fill="none" stroke="#ff9800" stroke-width="20" 
                    :stroke-dasharray="pieDashArray" stroke-dashoffset="0" transform="rotate(-90 50 50)" />
                  <circle cx="50" cy="50" r="40" fill="none" stroke="#4caf50" stroke-width="20" 
                    :stroke-dasharray="pieDashArray" :stroke-dashoffset="pieDashOffset" transform="rotate(-90 50 50)" />
                </svg>
                <div class="pie-center">
                  <div class="pie-percentage">{{ Math.round(completionRate.onTimeRate * 100) }}%</div>
                  <div class="pie-label">准时率</div>
                </div>
              </div>
              <div class="pie-legend">
                <div class="legend-item clickable-legend" @click="openDetailModal('onTime', '准时完成')">
                  <div class="legend-color legend-color-ontime"></div>
                  <span>准时完成: {{ completionRate.onTimeCount }}单</span>
                </div>
                <div class="legend-item clickable-legend" @click="openDetailModal('delayed', '延期完成')">
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
            <div class="vertical-bar-chart">
              <div class="vertical-chart-wrapper">
                <div class="vertical-chart-yaxis">
                  <div v-for="tick in topRepairYAxisTicks" :key="tick" class="v-yaxis-tick">{{ tick }}</div>
                </div>
                <div class="vertical-chart-content">
                  <div class="vertical-chart-grid">
                    <div v-for="tick in topRepairYAxisTicks" :key="'grid-' + tick" class="v-grid-line"></div>
                  </div>
                  <div class="vertical-bars-container">
                    <div v-for="(item, index) in topRepairs" :key="index" class="vertical-bar-col clickable-bar" @click="openProjectDetail(item.name, 'repair')">
                      <div class="v-bar-track">
                        <div class="v-bar-fill" :style="{ height: getTopRepairBarHeight(item.value) + '%' }">
                          <span class="v-bar-value">{{ item.value }}</span>
                        </div>
                      </div>
                      <div class="v-bar-label-wrapper">
                        <span 
                          class="v-bar-label-slanted" 
                          :style="{ fontSize: getLabelFontSize(item.name) + 'px' }"
                          :title="item.name"
                        >{{ item.name }}</span>
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
    </div>

    <div class="loading" v-else>
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <div class="modal-overlay" v-if="showDetailModal" @click.self="closeDetailModal">
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">{{ detailModalTitle }}</h3>
          <button class="modal-close" @click="closeDetailModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="detail-loading" v-if="detailLoading">
            <div class="loading-spinner small"></div>
            <span>加载中...</span>
          </div>
          <div class="detail-content" v-else>
            <div class="detail-stats">
              <span class="detail-total">共 {{ detailTotal }} 条记录</span>
            </div>
            <div class="detail-table-wrapper">
              <table class="detail-table">
                <thead>
                  <tr>
                    <th>序号</th>
                    <th>工单类型</th>
                    <th>工单编号</th>
                    <th>所属项目</th>
                    <th>运维人员</th>
                    <th>计划开始</th>
                    <th>计划结束</th>
                    <th>状态</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in detailData" :key="index">
                    <td>{{ index + 1 }}</td>
                    <td>{{ item.orderType }}</td>
                    <td>{{ item.orderNumber }}</td>
                    <td>{{ item.projectName }}</td>
                    <td>{{ item.maintenancePersonnel }}</td>
                    <td>{{ item.planStartDate }}</td>
                    <td>{{ item.planEndDate }}</td>
                    <td>
                      <span :class="['status-tag', getStatusClass(item.status)]">{{ getDisplayStatus(item.status) }}</span>
                    </td>
                  </tr>
                  <tr v-if="detailData.length === 0">
                    <td colspan="8" class="no-data">暂无数据</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onUnmounted, computed, inject } from 'vue'
import { statisticsService, StatisticsOverview, CompletionRate, TopProject, EmployeeStats, WorkOrderDetail } from '@/services/statistics'

// TODO: 统计页面 - 考虑加入数据导出功能(Excel/PDF)
// FIXME: 图表组件应该抽成独立的可复用组件
// TODO: 全屏模式下ESC键退出功能
export default defineComponent({
  name: 'StatisticsPage',
  setup() {
    const selectedYear = ref<number>(new Date().getFullYear())
    const currentYear = new Date().getFullYear()
    const availableYears = Array.from({ length: 5 }, (_, i) => currentYear - 2 + i)
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
    
    const showDetailModal = ref<boolean>(false)
    const detailModalTitle = ref<string>('')
    const detailLoading = ref<boolean>(false)
    const detailData = ref<WorkOrderDetail[]>([])
    const detailTotal = ref<number>(0)
    const currentDataType = ref<string>('')
    const currentEmployeeName = ref<string>('')
    const currentProjectName = ref<string>('')
    const currentOrderType = ref<string>('')
    
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

    const getTopRepairBarHeight = (value: number) => {
      if (maxTopRepairValue.value === 0) return 0
      return (value / maxTopRepairValue.value) * 100
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

    const getLabelFontSize = (name: string) => {
      if (!name) return 10
      const len = name.length
      if (len <= 4) return 12
      if (len <= 6) return 10
      if (len <= 8) return 9
      if (len <= 10) return 8
      return 7
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
      window.addEventListener('user-changed', handleUserChanged)
    })

    onUnmounted(() => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange)
      window.removeEventListener('user-changed', handleUserChanged)
    })

    const handleUserChanged = () => {
      handleYearChange()
    }

    const openDetailModal = async (dataType: string, title: string) => {
      currentDataType.value = dataType
      currentEmployeeName.value = ''
      currentProjectName.value = ''
      currentOrderType.value = ''
      detailModalTitle.value = title
      showDetailModal.value = true
      await fetchDetailData()
    }

    const openEmployeeDetail = async (employeeName: string, orderType?: string) => {
      currentDataType.value = 'employee'
      currentEmployeeName.value = employeeName
      currentProjectName.value = ''
      currentOrderType.value = orderType || ''
      detailModalTitle.value = `${employeeName} - 工单详情`
      showDetailModal.value = true
      await fetchDetailData()
    }

    const openProjectDetail = async (projectName: string, orderType?: string) => {
      currentDataType.value = 'project'
      currentProjectName.value = projectName
      currentEmployeeName.value = ''
      currentOrderType.value = orderType || ''
      detailModalTitle.value = `${projectName} - 工单详情`
      showDetailModal.value = true
      await fetchDetailData()
    }

    const closeDetailModal = () => {
      showDetailModal.value = false
      detailData.value = []
      detailTotal.value = 0
    }

    const fetchDetailData = async () => {
      detailLoading.value = true
      try {
        const params: any = {
          year: selectedYear.value,
          data_type: currentDataType.value,
          page: 1,
          page_size: 10000
        }
        if (currentEmployeeName.value) {
          params.employee_name = currentEmployeeName.value
        }
        if (currentProjectName.value) {
          params.project_name = currentProjectName.value
        }
        if (currentOrderType.value) {
          params.order_type = currentOrderType.value
        }
        console.log('fetchDetailData params:', params)
        const response = await statisticsService.getStatisticsDetail(params)
        console.log('fetchDetailData response:', response)
        console.log('response.data:', response?.data)
        console.log('response.total:', response?.total)
        detailData.value = response?.data || []
        detailTotal.value = response?.total || 0
        console.log('detailData:', detailData.value)
        console.log('detailTotal:', detailTotal.value)
      } catch (error) {
        console.error('获取详细数据失败:', error)
        detailData.value = []
        detailTotal.value = 0
      } finally {
        detailLoading.value = false
      }
    }

    const getStatusClass = (status: string) => {
      if (status === '已确认' || status === '已完成') return 'status-completed'
      if (status === '待确认') return 'status-in-progress'
      if (status === '未进行' || status === '已退回') return 'status-pending'
      return 'status-default'
    }

    const getDisplayStatus = (status: string) => {
      if (status === '已确认' || status === '已完成') return '已完成'
      if (status === '待确认') return '待确认'
      if (status === '未进行' || status === '已退回') return '待处理'
      return status
    }

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
      getTopRepairBarHeight,
      pieDashArray,
      pieDashOffset,
      truncateName,
      getLabelFontSize,
      toggleFullscreen,
      handleYearChange,
      showDetailModal,
      detailModalTitle,
      detailLoading,
      detailData,
      detailTotal,
      openDetailModal,
      openEmployeeDetail,
      openProjectDetail,
      closeDetailModal,
      getStatusClass,
      getDisplayStatus
    }
  }
})
</script>

<style scoped>
.statistics-page {
  padding: 20px 0;
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
  border-radius: 0;
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
  grid-template-columns: repeat(3, 1fr);
  gap: 1px;
  background: #e0e0e0;
}

.mini-card {
  background: white;
  border-radius: 0;
  padding: 16px;
  box-shadow: none;
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
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 1px;
  background: #e0e0e0;
  min-height: 300px;
}

.stat-card {
  background: white;
  border-radius: 0;
  padding: 24px;
  box-shadow: none;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: transform 0.2s, box-shadow 0.2s;
  min-height: 0;
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
  min-height: 0;
  overflow: hidden;
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
  min-height: 0;
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
  display: flex;
  flex-direction: column;
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
  flex: 1;
  justify-content: space-evenly;
  height: 100%;
}

.horizontal-bar-item {
  display: flex;
  align-items: center;
  flex: 1;
  min-height: 16px;
  max-height: 28px;
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
  height: 100%;
  max-height: 18px;
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
  background: #5470c6;
}

.bar-fill-red {
  background: #5470c6;
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
  background: #4caf50;
}

.legend-color-delayed {
  background: #ff9800;
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

.vertical-bar-chart {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.vertical-chart-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  min-height: 0;
}

.vertical-chart-yaxis {
  display: flex;
  flex-direction: column-reverse;
  justify-content: space-between;
  position: absolute;
  left: 0;
  top: 0;
  bottom: 24px;
  width: 40px;
  padding: 0 4px;
}

.v-yaxis-tick {
  font-size: 9px;
  color: #999;
  text-align: right;
  height: 20px;
  line-height: 20px;
}

.vertical-chart-content {
  flex: 1;
  position: relative;
  margin-left: 40px;
  display: flex;
  flex-direction: column;
  overflow: visible;
  min-height: 0;
}

.vertical-chart-grid {
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  height: 100px;
  display: flex;
  flex-direction: column-reverse;
  justify-content: space-between;
  pointer-events: none;
}

.v-grid-line {
  width: 100%;
  border-bottom: 1px dashed #e8e8e8;
  height: 20px;
}

.vertical-bars-container {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  position: relative;
  z-index: 1;
  margin-bottom: 35px;
  margin-top: auto;
  flex: 1;
  width: 100%;
}

.vertical-bar-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  max-width: 60px;
  min-width: 30px;
}

.v-bar-track {
  width: 60%;
  max-width: 24px;
  min-width: 12px;
  height: 100px;
  background: #f0f0f0;
  border-radius: 3px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  overflow: hidden;
  margin: 0 auto;
  flex-shrink: 0;
}

.v-bar-fill {
  width: 100%;
  background: #5470c6;
  border-radius: 3px 3px 0 0;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 4px;
  min-height: 20px;
  transition: height 0.3s ease;
  margin: 0 auto;
}

.v-bar-value {
  font-size: 10px;
  font-weight: 600;
  color: white;
}

.v-bar-label {
  margin-top: 4px;
  font-size: 10px;
  color: #333;
  text-align: center;
  max-width: 50px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.v-bar-label-wrapper {
  width: 80px;
  min-height: 20px;
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  overflow: visible;
  margin-top: 8px;
  margin-left: 10px;
}

.v-bar-label-slanted {
  display: inline-block;
  color: #333;
  white-space: normal;
  transform: rotate(-45deg);
  transform-origin: top left;
  text-align: left;
  line-height: 1.1;
  word-break: break-all;
  max-width: 48px;
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
  padding: 16px 24px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

:fullscreen .top-bar {
  flex-shrink: 0;
  padding: 12px 20px;
  margin-bottom: 12px;
}

:fullscreen .content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
  overflow: hidden;
}

:fullscreen .top-cards-section {
  flex-shrink: 0;
  gap: 1px;
  grid-template-columns: repeat(3, 1fr);
}

:fullscreen .mini-card {
  padding: 14px 16px;
}

:fullscreen .mini-card-value {
  font-size: 32px;
}

:fullscreen .mini-card-label {
  font-size: 12px;
}

:fullscreen .cards-section {
  flex: 1;
  min-height: 0;
  gap: 1px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(2, 1fr);
  overflow: hidden;
}

:fullscreen .stat-card {
  padding: 16px 20px;
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
  padding: 12px 16px;
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

:fullscreen .chart-caption {
  font-size: 1rem;
  margin-bottom: 8px;
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
  margin-bottom: 4px;
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
  gap: 6px;
}

:fullscreen .horizontal-bar-item {
  height: auto;
  flex: 1 1 auto;
  min-height: 22px;
  max-height: 32px;
  display: flex;
  align-items: center;
}

:fullscreen .bar-label {
  font-size: 12px;
  width: 70px;
}

:fullscreen .bar-track {
  height: 18px;
}

:fullscreen .bar-value {
  font-size: 11px;
}

:fullscreen .y-axis-tick {
  font-size: 10px;
}

:fullscreen .pie-chart-wrapper {
  min-height: 0;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 48px;
}

:fullscreen .pie-chart-container {
  position: relative;
}

:fullscreen .pie-svg {
  width: 240px;
  height: 240px;
}

:fullscreen .pie-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

:fullscreen .pie-percentage {
  font-size: 44px;
}

:fullscreen .pie-label {
  font-size: 20px;
}

:fullscreen .pie-legend {
  gap: 12px;
}

:fullscreen .legend-item {
  font-size: 14px;
  gap: 10px;
}

:fullscreen .legend-color {
  width: 18px;
  height: 18px;
}

:fullscreen .vertical-bar-chart {
  min-height: 150px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

:fullscreen .vertical-chart-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

:fullscreen .vertical-chart-yaxis {
  bottom: 24px;
  width: 40px;
}

:fullscreen .v-yaxis-tick {
  font-size: 10px;
  height: 20px;
  line-height: 20px;
}

:fullscreen .vertical-chart-content {
  margin-left: 40px;
  overflow: visible;
}

:fullscreen .vertical-chart-grid {
  height: 100px;
}

:fullscreen .v-grid-line {
  height: 20px;
}

:fullscreen .vertical-bars-container {
  margin-bottom: 40px;
  margin-top: auto;
  flex: 1;
  width: 100%;
}

:fullscreen .vertical-bar-col {
  max-width: 60px;
  min-width: 30px;
}

:fullscreen .v-bar-track {
  height: 100px;
  width: 60%;
  max-width: 24px;
  min-width: 12px;
}

:fullscreen .v-bar-fill {
  min-height: 18px;
  padding-top: 3px;
  width: 100%;
}

:fullscreen .v-bar-value {
  font-size: 10px;
}

:fullscreen .v-bar-label {
  font-size: 10px;
  margin-top: 4px;
}

:fullscreen .v-bar-label-wrapper {
  min-height: 25px;
  width: 100px;
  margin-top: 10px;
  margin-left: 15px;
}

:fullscreen .v-bar-label-slanted {
  font-size: 11px;
  max-width: 54px;
}

:fullscreen .employee-no-data {
  font-size: 14px;
}

.clickable {
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.clickable:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.clickable-bar {
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.clickable-bar:hover {
  background-color: rgba(84, 112, 198, 0.1);
}

.clickable-legend {
  cursor: pointer;
  transition: opacity 0.15s ease;
}

.clickable-legend:hover {
  opacity: 0.8;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: white;
  border-radius: 12px;
  width: 95%;
  max-width: 1400px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #e0e0e0;
  flex-shrink: 0;
}

.modal-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 0;
  line-height: 1;
}

.modal-close:hover {
  color: #333;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.detail-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #666;
  gap: 12px;
}

.loading-spinner.small {
  width: 24px;
  height: 24px;
  border-width: 2px;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-total {
  font-size: 14px;
  color: #666;
}

.detail-table-wrapper {
  overflow-x: auto;
}

.detail-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.detail-table th,
.detail-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.detail-table th {
  background: #f5f7fa;
  font-weight: 600;
  color: #333;
  white-space: nowrap;
}

.detail-table tr:hover {
  background: #f9f9f9;
}

.no-data {
  text-align: center;
  color: #999;
  padding: 40px;
}

.status-tag {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-completed {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-in-progress {
  background: #e3f2fd;
  color: #1565c0;
}

.status-pending {
  background: #fff3e0;
  color: #e65100;
}

.status-overdue {
  background: #ffebee;
  color: #c62828;
}

.status-default {
  background: #f5f5f5;
  color: #666;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  padding-top: 16px;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  background: white;
  color: #333;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #f5f5f5;
  border-color: #ccc;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
}
</style>
