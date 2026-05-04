<template>
  <div class="statistics-page">
    <div class="top-bar">
      <div class="year-selector">
        <label
          for="search_yearSelect"
          class="year-label"
        >年度选择：</label>
        <select
          id="search_yearSelect"
          v-model="selectedYear"
          name="search_yearSelect"
          class="year-select"
          @change="handleYearChange"
        >
          <option
            v-for="year in availableYears"
            :key="year"
            :value="year"
          >
            {{ year }}
          </option>
        </select>
      </div>
      <div class="refresh-controls">
        <button
          class="btn btn-refresh"
          @click="handleYearChange"
        >
          刷新
        </button>
        <button
          class="btn btn-fullscreen"
          @click="toggleFullscreen"
        >
          {{ isFullscreen ? '退出全屏' : '全屏' }}
        </button>
      </div>
    </div>

    <div
      v-if="!loading"
      class="content"
    >
      <div class="top-cards-section">
        <div
          class="mini-card mini-card-warning clickable"
          @click="openDetailModal('nearDue', '临期工单')"
        >
          <div class="mini-card-value">
            {{ overviewData.nearDueCount }}
          </div>
          <div class="mini-card-label">
            临期工单
          </div>
        </div>
        <div
          class="mini-card mini-card-danger clickable"
          @click="openDetailModal('overdue', '超期工单')"
        >
          <div class="mini-card-value">
            {{ overviewData.overdueCount }}
          </div>
          <div class="mini-card-label">
            超期工单
          </div>
        </div>
        <div
          class="mini-card mini-card-success clickable"
          @click="openDetailModal('yearCompleted', '本年完成')"
        >
          <div class="mini-card-value">
            {{ overviewData.yearCompletedCount }}
          </div>
          <div class="mini-card-label">
            本年完成
          </div>
        </div>
        <div
          class="mini-card mini-card-info clickable"
          @click="openDetailModal('regularInspection', '定期巡检单')"
        >
          <div class="mini-card-value">
            {{ overviewData.regularInspectionCount }}
          </div>
          <div class="mini-card-label">
            定期巡检单
          </div>
        </div>
        <div
          class="mini-card mini-card-purple clickable"
          @click="openDetailModal('temporaryRepair', '临时维修单')"
        >
          <div class="mini-card-value">
            {{ overviewData.temporaryRepairCount }}
          </div>
          <div class="mini-card-label">
            临时维修单
          </div>
        </div>
        <div
          class="mini-card mini-card-cyan clickable"
          @click="openDetailModal('spotWork', '零星用工单')"
        >
          <div class="mini-card-value">
            {{ overviewData.spotWorkCount }}
          </div>
          <div class="mini-card-label">
            零星用工单
          </div>
        </div>
      </div>

      <div class="cards-section">
        <div class="stat-card card-total employee-chart-card">
          <div class="employee-chart-container">
            <div class="chart-caption">
              本年度工单数量（{{ selectedYear }}）
            </div>
            <div class="horizontal-bar-chart">
              <div class="chart-y-axis">
                <div
                  v-for="tick in yAxisTicks"
                  :key="tick"
                  class="y-axis-tick"
                >
                  {{ tick }}
                </div>
              </div>
              <div class="chart-content">
                <div class="chart-grid">
                  <div
                    v-for="tick in yAxisTicks"
                    :key="'grid-' + tick"
                    class="grid-line"
                  />
                </div>
                <div class="horizontal-bars">
                  <div
                    v-for="(employee, index) in employeeStats.employees"
                    :key="index"
                    class="horizontal-bar-item clickable-bar"
                    @click="openEmployeeDetail(employee.name)"
                  >
                    <div class="bar-label">
                      {{ employee.name }}
                    </div>
                    <div class="bar-track">
                      <div
                        class="bar-fill"
                        :style="{ width: getEmployeeBarWidth(employee.count) + '%' }"
                      >
                        <span class="bar-value">{{ employee.count }}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div
                  v-if="employeeStats.employees.length === 0"
                  class="employee-no-data"
                >
                  暂无数据
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="stat-card card-inspection inspection-chart-card">
          <div class="employee-chart-container">
            <div class="chart-caption">
              定期巡检单完成数量（{{ selectedYear }}）
            </div>
            <div class="horizontal-bar-chart">
              <div class="chart-y-axis">
                <div
                  v-for="tick in inspectionYAxisTicks"
                  :key="tick"
                  class="y-axis-tick"
                >
                  {{ tick }}
                </div>
              </div>
              <div class="chart-content">
                <div class="chart-grid">
                  <div
                    v-for="tick in inspectionYAxisTicks"
                    :key="'grid-' + tick"
                    class="grid-line"
                  />
                </div>
                <div class="horizontal-bars">
                  <div
                    v-for="(item, index) in inspectionStats.employees"
                    :key="index"
                    class="horizontal-bar-item clickable-bar"
                    @click="openEmployeeDetail(item.name, 'inspection')"
                  >
                    <div class="bar-label">
                      {{ item.name }}
                    </div>
                    <div class="bar-track">
                      <div
                        class="bar-fill bar-fill-green"
                        :style="{ width: getInspectionBarWidth(item.count) + '%' }"
                      >
                        <span class="bar-value">{{ item.count }}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div
                  v-if="inspectionStats.employees.length === 0"
                  class="employee-no-data"
                >
                  暂无数据
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="stat-card card-repair repair-chart-card">
          <div class="employee-chart-container">
            <div class="chart-caption">
              临时维修单完成数量（{{ selectedYear }}）
            </div>
            <div class="horizontal-bar-chart">
              <div class="chart-y-axis">
                <div
                  v-for="tick in repairYAxisTicks"
                  :key="tick"
                  class="y-axis-tick"
                >
                  {{ tick }}
                </div>
              </div>
              <div class="chart-content">
                <div class="chart-grid">
                  <div
                    v-for="tick in repairYAxisTicks"
                    :key="'grid-' + tick"
                    class="grid-line"
                  />
                </div>
                <div class="horizontal-bars">
                  <div
                    v-for="(item, index) in repairStats.employees"
                    :key="index"
                    class="horizontal-bar-item clickable-bar"
                    @click="openEmployeeDetail(item.name, 'repair')"
                  >
                    <div class="bar-label">
                      {{ item.name }}
                    </div>
                    <div class="bar-track">
                      <div
                        class="bar-fill bar-fill-red"
                        :style="{ width: getRepairBarWidth(item.count) + '%' }"
                      >
                        <span class="bar-value">{{ item.count }}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div
                  v-if="repairStats.employees.length === 0"
                  class="employee-no-data"
                >
                  暂无数据
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="stat-card card-labor spotwork-chart-card">
          <div class="employee-chart-container">
            <div class="chart-caption">
              零星用工单完成数量（{{ selectedYear }}）
            </div>
            <div class="horizontal-bar-chart">
              <div class="chart-y-axis">
                <div
                  v-for="tick in spotworkYAxisTicks"
                  :key="tick"
                  class="y-axis-tick"
                >
                  {{ tick }}
                </div>
              </div>
              <div class="chart-content">
                <div class="chart-grid">
                  <div
                    v-for="tick in spotworkYAxisTicks"
                    :key="'grid-' + tick"
                    class="grid-line"
                  />
                </div>
                <div class="horizontal-bars">
                  <div
                    v-for="(item, index) in spotworkStats.employees"
                    :key="index"
                    class="horizontal-bar-item clickable-bar"
                    @click="openEmployeeDetail(item.name, 'spotwork')"
                  >
                    <div class="bar-label">
                      {{ item.name }}
                    </div>
                    <div class="bar-track">
                      <div
                        class="bar-fill"
                        :style="{ width: getSpotworkBarWidth(item.count) + '%' }"
                      >
                        <span class="bar-value">{{ item.count }}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div
                  v-if="spotworkStats.employees.length === 0"
                  class="employee-no-data"
                >
                  暂无数据
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="stat-card card-total employee-chart-card">
          <div class="employee-chart-container">
            <div class="chart-caption">
              准时完成情况分布（{{ selectedYear }}）
            </div>
            <div class="pie-chart-wrapper">
              <div
                class="pie-chart-container clickable"
                @click="openDetailModal('onTime', '准时完成')"
              >
                <svg
                  class="pie-svg"
                  viewBox="0 0 100 100"
                >
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    fill="none"
                    stroke="#ff9800"
                    stroke-width="20"
                    :stroke-dasharray="pieDashArray"
                    stroke-dashoffset="0"
                    transform="rotate(-90 50 50)"
                  />
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    fill="none"
                    stroke="#4caf50"
                    stroke-width="20"
                    :stroke-dasharray="pieDashArray"
                    :stroke-dashoffset="pieDashOffset"
                    transform="rotate(-90 50 50)"
                  />
                </svg>
                <div class="pie-center">
                  <div class="pie-percentage">
                    {{ Math.round(completionRate.onTimeRate * 100) }}%
                  </div>
                  <div class="pie-label">
                    准时率
                  </div>
                </div>
              </div>
              <div class="pie-legend">
                <div
                  class="legend-item clickable-legend"
                  @click="openDetailModal('onTime', '准时完成')"
                >
                  <div class="legend-color legend-color-ontime" />
                  <span>准时完成: {{ completionRate.onTimeCount }}单</span>
                </div>
                <div
                  class="legend-item clickable-legend"
                  @click="openDetailModal('delayed', '延期完成')"
                >
                  <div class="legend-color legend-color-delayed" />
                  <span>延期完成: {{ completionRate.delayedCount }}单</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="stat-card card-inspection inspection-chart-card">
          <div class="employee-chart-container">
            <div class="chart-caption">
              临时维修单前五（{{ selectedYear }}）
            </div>
            <div class="vertical-bar-chart">
              <div class="vertical-chart-wrapper">
                <div class="vertical-chart-yaxis">
                  <div
                    v-for="tick in topRepairYAxisTicks"
                    :key="tick"
                    class="v-yaxis-tick"
                  >
                    {{ tick }}
                  </div>
                </div>
                <div class="vertical-chart-content">
                  <div class="vertical-chart-grid">
                    <div
                      v-for="tick in topRepairYAxisTicks"
                      :key="'grid-' + tick"
                      class="v-grid-line"
                    />
                  </div>
                  <div class="vertical-bars-container">
                    <div
                      v-for="(item, index) in topRepairs"
                      :key="index"
                      class="vertical-bar-col clickable-bar"
                      @click="openProjectDetail(item.name, 'repair')"
                    >
                      <div class="v-bar-track">
                        <div
                          class="v-bar-fill"
                          :style="{ height: getTopRepairBarHeight(item.value) + '%' }"
                        >
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
                  <div
                    v-if="topRepairs.length === 0"
                    class="employee-no-data"
                  >
                    暂无数据
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div
      v-else
      class="loading"
    >
      <div class="loading-spinner" />
      <p>加载中...</p>
    </div>

    <div
      v-if="showDetailModal"
      class="modal-overlay"
      @click.self="closeDetailModal"
    >
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">
            {{ detailModalTitle }}
          </h3>
          <button
            class="modal-close"
            @click="closeDetailModal"
          >
            &times;
          </button>
        </div>
        <div class="modal-body">
          <div
            v-if="detailLoading"
            class="detail-loading"
          >
            <div class="loading-spinner small" />
            <span>加载中...</span>
          </div>
          <div
            v-else
            class="detail-content"
          >
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
                  <tr
                    v-for="(item, index) in detailData"
                    :key="index"
                  >
                    <td>{{ (detailCurrentPage - 1) * detailPageSize + index + 1 }}</td>
                    <td>{{ item.orderType }}</td>
                    <td>{{ item.orderNumber }}</td>
                    <td>{{ item.projectName }}</td>
                    <td>{{ item.maintenancePersonnel }}</td>
                    <td>{{ item.planStartDate }}</td>
                    <td>{{ item.planEndDate }}</td>
                    <td>
                      <span :class="['status-tag', getStatusClass(item.status)]">{{
                        getDisplayStatus(item.status)
                      }}</span>
                    </td>
                  </tr>
                  <tr v-if="detailData.length === 0">
                    <td
                      colspan="8"
                      class="no-data"
                    >
                      暂无数据
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div
          v-if="detailTotal > 0"
          class="modal-footer"
        >
          <div class="pagination">
            <button
              class="page-btn"
              :disabled="detailCurrentPage === 1"
              @click="handleDetailPageChange(1)"
            >
              首页
            </button>
            <button
              class="page-btn"
              :disabled="detailCurrentPage === 1"
              @click="handleDetailPageChange(detailCurrentPage - 1)"
            >
              上一页
            </button>
            <span class="page-info">第 {{ detailCurrentPage }} / {{ detailTotalPages }} 页</span>
            <button
              class="page-btn"
              :disabled="detailCurrentPage >= detailTotalPages"
              @click="handleDetailPageChange(detailCurrentPage + 1)"
            >
              下一页
            </button>
            <button
              class="page-btn"
              :disabled="detailCurrentPage >= detailTotalPages"
              @click="handleDetailPageChange(detailTotalPages)"
            >
              末页
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onUnmounted, computed, inject } from 'vue'
import {
  statisticsService,
  StatisticsOverview,
  CompletionRate,
  TopProject,
  EmployeeStats,
  WorkOrderDetail,
} from '@/services/statistics'

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
      yearCompletedCount: 0,
    })
    const completionRate = ref<CompletionRate>({
      year: selectedYear.value,
      onTimeRate: 0,
      onTimeCount: 0,
      delayedCount: 0,
      totalCount: 0,
    })
    const topProjects = ref<TopProject[]>([])
    const topRepairs = ref<TopProject[]>([])
    const employeeStats = ref<EmployeeStats>({
      year: selectedYear.value,
      employees: [],
      total: 0,
    })
    const inspectionStats = ref<EmployeeStats>({
      year: selectedYear.value,
      employees: [],
      total: 0,
    })
    const repairStats = ref<EmployeeStats>({
      year: selectedYear.value,
      employees: [],
      total: 0,
    })
    const spotworkStats = ref<EmployeeStats>({
      year: selectedYear.value,
      employees: [],
      total: 0,
    })
    const loading = ref<boolean>(false)
    const isFullscreen = ref<boolean>(false)

    const showDetailModal = ref<boolean>(false)
    const detailModalTitle = ref<string>('')
    const detailLoading = ref<boolean>(false)
    const detailData = ref<WorkOrderDetail[]>([])
    const detailTotal = ref<number>(0)
    const detailCurrentPage = ref<number>(1)
    const detailPageSize = ref<number>(10)
    const currentDataType = ref<string>('')
    const currentEmployeeName = ref<string>('')
    const currentProjectName = ref<string>('')
    const currentOrderType = ref<string>('')

    const setFullscreenMode = inject<(value: boolean) => void>('setFullscreenMode')

    const detailTotalPages = computed(() => {
      return Math.ceil(detailTotal.value / detailPageSize.value) || 1
    })

    const maxProjectValue = computed(() => {
      if (topRepairs.value.length === 0) return 1
      return Math.max(...topRepairs.value.map((p) => p.value), 1)
    })

    const maxEmployeeValue = computed(() => {
      if (employeeStats.value.employees.length === 0) return 10
      return Math.max(...employeeStats.value.employees.map((e) => e.count), 10)
    })

    const maxInspectionValue = computed(() => {
      if (inspectionStats.value.employees.length === 0) return 10
      return Math.max(...inspectionStats.value.employees.map((e) => e.count), 10)
    })

    const maxRepairValue = computed(() => {
      if (repairStats.value.employees.length === 0) return 10
      return Math.max(...repairStats.value.employees.map((e) => e.count), 10)
    })

    const maxSpotworkValue = computed(() => {
      if (spotworkStats.value.employees.length === 0) return 10
      return Math.max(...spotworkStats.value.employees.map((e) => e.count), 10)
    })

    const maxTopRepairValue = computed(() => {
      if (topRepairs.value.length === 0) return 10
      return Math.max(...topRepairs.value.map((e) => e.value), 10)
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
        // 串行加载统计数据，避免并发请求触发后端限流
        overviewData.value = await statisticsService.getStatisticsOverview(selectedYear.value)
        completionRate.value = await statisticsService.getCompletionRate(selectedYear.value)
        topProjects.value = await statisticsService.getTopProjects(selectedYear.value, 5)
        topRepairs.value = await statisticsService.getTopRepairs(selectedYear.value, 5)
        employeeStats.value = await statisticsService.getEmployeeStats(selectedYear.value)
        inspectionStats.value = await statisticsService.getInspectionStats(selectedYear.value)
        repairStats.value = await statisticsService.getRepairStats(selectedYear.value)
        spotworkStats.value = await statisticsService.getSpotworkStats(selectedYear.value)
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
      detailCurrentPage.value = 1
      showDetailModal.value = true
      await fetchDetailData()
    }

    const openEmployeeDetail = async (employeeName: string, orderType?: string) => {
      currentDataType.value = 'employee'
      currentEmployeeName.value = employeeName
      currentProjectName.value = ''
      currentOrderType.value = orderType || ''
      detailModalTitle.value = `${employeeName} - 工单详情`
      detailCurrentPage.value = 1
      showDetailModal.value = true
      await fetchDetailData()
    }

    const openProjectDetail = async (projectName: string, orderType?: string) => {
      currentDataType.value = 'project'
      currentProjectName.value = projectName
      currentEmployeeName.value = ''
      currentOrderType.value = orderType || ''
      detailModalTitle.value = `${projectName} - 工单详情`
      detailCurrentPage.value = 1
      showDetailModal.value = true
      await fetchDetailData()
    }

    const closeDetailModal = () => {
      showDetailModal.value = false
      detailData.value = []
      detailTotal.value = 0
      detailCurrentPage.value = 1
    }

    const fetchDetailData = async () => {
      detailLoading.value = true
      try {
        const params: any = {
          year: selectedYear.value,
          data_type: currentDataType.value,
          page: detailCurrentPage.value,
          page_size: detailPageSize.value,
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
        const response = await statisticsService.getStatisticsDetail(params)
        detailData.value = response?.data || []
        detailTotal.value = response?.total || 0
      } catch (error) {
        console.error('获取详细数据失败:', error)
        detailData.value = []
        detailTotal.value = 0
      } finally {
        detailLoading.value = false
      }
    }

    const handleDetailPageChange = async (page: number) => {
      detailCurrentPage.value = page
      await fetchDetailData()
    }

    const getStatusClass = (status: string) => {
      if (status === '已完成') return 'status-completed'
      if (status === '待确认') return 'status-in-progress'
      if (status === '执行中' || status === '已退回') return 'status-pending'
      return 'status-default'
    }

    const getDisplayStatus = (status: string) => {
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
      detailCurrentPage,
      detailPageSize,
      detailTotalPages,
      openDetailModal,
      openEmployeeDetail,
      openProjectDetail,
      closeDetailModal,
      handleDetailPageChange,
      getStatusClass,
      getDisplayStatus,
    }
  },
})
</script>

<style scoped>
.statistics-page {
  padding: 0;
  background: var(--color-bg-page);
  min-height: 100vh;
  font-family: var(--font-sans);
  box-sizing: border-box;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-4);
}

.year-selector {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.year-label {
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  color: var(--color-text-regular);
}

.year-select {
  padding: var(--space-1) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  background: var(--color-bg-card);
  color: var(--color-text-primary);
  outline: none;
  font-family: var(--font-mono);
}

.year-select:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px var(--color-primary-subtle);
}

.refresh-controls {
  display: flex;
  gap: var(--space-2);
}

.btn {
  padding: var(--space-1) var(--space-3);
  border: none;
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  gap: var(--space-1);
  color: #fff;
}

.btn-refresh {
  background: var(--color-primary);
}

.btn-refresh:hover {
  background: var(--color-primary-dark);
}

.btn-fullscreen {
  background: var(--color-info);
}

.btn-fullscreen:hover {
  background: #4a6a8a;
}

.content {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.top-cards-section {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-3);
}

.mini-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  text-align: center;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.mini-card.clickable {
  cursor: pointer;
}

.mini-card.clickable:hover {
  border-color: var(--color-border-dark);
  box-shadow: var(--shadow-sm);
}

.mini-card-value {
  font-family: var(--font-mono);
  font-size: var(--text-3xl);
  font-weight: var(--weight-bold);
  margin-bottom: var(--space-1);
  line-height: 1;
}

.mini-card-label {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  letter-spacing: 0.04em;
}

.mini-card-warning .mini-card-value {
  color: var(--color-warning);
}

.mini-card-danger .mini-card-value {
  color: var(--color-danger);
}

.mini-card-success .mini-card-value {
  color: var(--color-success);
}

.mini-card-info .mini-card-value {
  color: var(--color-info);
}

.mini-card-purple .mini-card-value {
  color: var(--color-primary);
}

.mini-card-cyan .mini-card-value {
  color: var(--color-accent);
}

.cards-section {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: var(--space-3);
  min-height: 300px;
}

.stat-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  display: flex;
  align-items: center;
  gap: var(--space-4);
  transition: border-color var(--transition-fast);
  min-height: 0;
}

.stat-card:hover {
  border-color: var(--color-border-dark);
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-total .card-icon {
  background: var(--color-primary-subtle);
  color: var(--color-primary);
}

.card-inspection .card-icon {
  background: var(--color-success-subtle);
  color: var(--color-success);
}

.card-repair .card-icon {
  background: var(--color-danger-subtle);
  color: var(--color-danger);
}

.card-labor .card-icon {
  background: var(--color-accent-subtle);
  color: var(--color-accent);
}

.card-content {
  flex: 1;
}

.card-label {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-2);
}

.card-value {
  font-family: var(--font-mono);
  font-size: var(--text-3xl);
  font-weight: var(--weight-bold);
  color: var(--color-text-primary);
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
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  overflow: hidden;
}

.chart-caption {
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  color: var(--color-text-primary);
  letter-spacing: -0.01em;
  margin-bottom: var(--space-2);
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
  margin-bottom: var(--space-1);
}

.y-axis-tick {
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--color-text-placeholder);
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
  border-left: 1px dashed var(--color-border-light);
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
  color: var(--color-text-regular);
  text-align: right;
  padding-right: var(--space-2);
  flex-shrink: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bar-track {
  flex: 1;
  height: 100%;
  max-height: 18px;
  background: var(--color-bg-page);
  border-radius: var(--radius-xs);
  overflow: hidden;
  position: relative;
}

.bar-fill {
  height: 100%;
  background: var(--color-primary);
  border-radius: var(--radius-xs);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 6px;
  min-width: 24px;
  transition: width 0.3s ease-out;
}

.bar-fill-green {
  background: var(--color-success);
}

.bar-fill-red {
  background: var(--color-danger);
}

.bar-value {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: var(--weight-semibold);
  color: white;
}

.pie-chart-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-6);
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
  font-family: var(--font-mono);
  font-size: var(--text-xl);
  font-weight: var(--weight-bold);
  color: var(--color-text-primary);
}

.pie-label {
  font-size: 10px;
  color: var(--color-text-secondary);
  margin-top: 2px;
}

.pie-legend {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 11px;
  color: var(--color-text-regular);
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: var(--radius-xs);
}

.legend-color-ontime {
  background: var(--color-success);
}

.legend-color-delayed {
  background: var(--color-warning);
}

.employee-no-data {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: var(--color-text-placeholder);
  font-size: var(--text-sm);
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
  padding: 0 var(--space-1);
}

.v-yaxis-tick {
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--color-text-placeholder);
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
  border-bottom: 1px dashed var(--color-border-light);
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
  background: var(--color-bg-page);
  border-radius: var(--radius-xs);
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  overflow: hidden;
  margin: 0 auto;
  flex-shrink: 0;
}

.v-bar-fill {
  width: 100%;
  background: var(--color-primary);
  border-radius: var(--radius-xs) var(--radius-xs) 0 0;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: var(--space-1);
  min-height: 20px;
  transition: height 0.3s ease-out;
  margin: 0 auto;
}

.v-bar-value {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: var(--weight-semibold);
  color: white;
}

.v-bar-label-wrapper {
  width: 80px;
  min-height: 20px;
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  overflow: visible;
  margin-top: var(--space-2);
  margin-left: 10px;
}

.v-bar-label-slanted {
  display: inline-block;
  color: var(--color-text-regular);
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
  width: 32px;
  height: 32px;
  border: 3px solid var(--color-border-light);
  border-top: 3px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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
    gap: var(--space-3);
  }
}

:fullscreen .statistics-page {
  min-height: 100vh;
  height: 100vh;
  width: 100vw;
  padding: var(--space-4);
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

:fullscreen .top-bar {
  flex-shrink: 0;
  padding: var(--space-2) var(--space-4);
  margin-bottom: var(--space-3);
}

:fullscreen .content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  min-height: 0;
  overflow: hidden;
}

:fullscreen .top-cards-section {
  flex-shrink: 0;
  gap: var(--space-3);
  grid-template-columns: repeat(3, 1fr);
}

:fullscreen .mini-card {
  padding: var(--space-3) var(--space-4);
}

:fullscreen .mini-card-value {
  font-size: var(--text-3xl);
}

:fullscreen .cards-section {
  flex: 1;
  min-height: 0;
  gap: var(--space-3);
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(2, 1fr);
  overflow: hidden;
}

:fullscreen .stat-card {
  padding: var(--space-4);
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
  padding: var(--space-3) var(--space-4);
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

:fullscreen .chart-caption {
  font-size: var(--text-sm);
  margin-bottom: var(--space-2);
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
  margin-bottom: var(--space-1);
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
  font-size: var(--text-xs);
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
  font-size: var(--text-lg);
}

:fullscreen .pie-legend {
  gap: var(--space-3);
}

:fullscreen .legend-item {
  font-size: var(--text-sm);
  gap: var(--space-2);
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
  font-size: var(--text-sm);
}

.clickable {
  cursor: pointer;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.clickable:hover {
  border-color: var(--color-border-dark);
  box-shadow: var(--shadow-sm);
}

.clickable-bar {
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.clickable-bar:hover {
  background-color: var(--color-primary-subtle);
}

.clickable-legend {
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.clickable-legend:hover {
  opacity: 0.75;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--color-bg-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
}

.modal-container {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  width: 95%;
  max-width: 1400px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-xl);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--color-border-light);
  flex-shrink: 0;
}

.modal-title {
  margin: 0;
  font-size: var(--text-lg);
  font-weight: var(--weight-semibold);
  color: var(--color-text-primary);
}

.modal-close {
  background: none;
  border: none;
  font-size: var(--text-xl);
  cursor: pointer;
  color: var(--color-text-secondary);
  padding: 0;
  line-height: 1;
  transition: color var(--transition-fast);
}

.modal-close:hover {
  color: var(--color-text-primary);
}

.modal-body {
  padding: var(--space-6);
  flex: 1;
  overflow-y: auto;
  min-height: 300px;
}

.modal-footer {
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--color-border-light);
  background: var(--color-bg-page);
  flex-shrink: 0;
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
}

.detail-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-10);
  color: var(--color-text-secondary);
  gap: var(--space-3);
}

.loading-spinner.small {
  width: 24px;
  height: 24px;
  border-width: 2px;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  height: 100%;
}

.detail-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-total {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.detail-table-wrapper {
  overflow-x: auto;
  overflow-y: auto;
  flex: 1;
  max-height: calc(90vh - 250px);
}

.detail-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);
}

.detail-table th,
.detail-table td {
  padding: var(--space-3) var(--space-4);
  text-align: left;
  border-bottom: 1px solid var(--color-border-light);
}

.detail-table th {
  background: var(--color-bg-page);
  font-weight: var(--weight-semibold);
  color: var(--color-text-regular);
  white-space: nowrap;
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.detail-table tr:hover {
  background: var(--color-bg-page);
}

.no-data {
  text-align: center;
  color: var(--color-text-placeholder);
  padding: var(--space-10);
}

.status-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--weight-medium);
}

.status-completed {
  background: var(--status-completed-bg);
  color: var(--status-completed-text);
}

.status-in-progress {
  background: var(--status-executing-bg);
  color: var(--status-executing-text);
}

.status-pending {
  background: var(--status-pending-bg);
  color: var(--status-pending-text);
}

.status-overdue {
  background: var(--status-overdue-bg);
  color: var(--status-overdue-text);
}

.status-default {
  background: var(--color-bg-page);
  color: var(--color-text-secondary);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--space-4);
  padding-top: var(--space-4);
}

.page-btn {
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-bg-card);
  color: var(--color-text-regular);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.page-btn:hover:not(:disabled) {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-info {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  font-family: var(--font-mono);
}
</style>
