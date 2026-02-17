<template>
  <div class="spare-parts-page">
    <div class="content">
      <div class="search-section">
        <div class="search-form">
          <div class="search-item">
            <label class="search-label">运维人员员：</label>
            <select class="search-select" v-model="searchForm.personnel">
              <option value="">全部</option>
              <option v-for="person in personnelList" :key="person" :value="person">{{ person }}</option>
            </select>
          </div>
          <div class="search-item">
            <label class="search-label">产品名称：</label>
            <SearchInput
              v-model="searchForm.productName"
              field-key="SparePartsManagement_productName"
              placeholder="请输入"
              @input="handleSearch"
            />
          </div>
          <div class="search-item">
            <label class="search-label">项目名称：</label>
            <select class="search-select" v-model="searchForm.projectName">
              <option value="">全部</option>
              <option v-for="project in projectList" :key="project" :value="project">{{ project }}</option>
            </select>
          </div>
        </div>
        <div class="action-buttons">
        </div>
      </div>

      <div class="table-section">
        <table class="data-table">
          <thead>
            <tr>
              <th>序号</th>
              <th>项目编号</th>
              <th>项目名称</th>
              <th>产品名称</th>
              <th>品牌</th>
              <th>产品型号</th>
              <th>领用数量</th>
              <th>运维人员</th>
              <th>领用时间</th>
              <th>单位</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="10" style="text-align: center; padding: 20px;">加载中...</td>
            </tr>
            <tr v-else-if="partsData.length === 0">
              <td colspan="10" style="text-align: center; padding: 20px;">暂无数据</td>
            </tr>
            <tr v-else v-for="(item, index) in partsData" :key="item.id" :class="{ 'even-row': index % 2 === 0 }">
              <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
              <td>{{ item.project_id || '-' }}</td>
              <td>{{ item.projectName || '-' }}</td>
              <td>{{ item.productName }}</td>
              <td>{{ item.brand || '-' }}</td>
              <td>{{ item.model || '-' }}</td>
              <td>{{ item.quantity }}</td>
              <td>{{ item.userName }}</td>
              <td>{{ formatDate(item.issueTime) }}</td>
              <td>{{ item.unit }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pagination-section">
        <div class="pagination-info">
          共 {{ totalElements }} 条记录
        </div>
        <div class="pagination-controls">
          <button class="page-btn page-nav" :disabled="currentPage === 1" @click="currentPage--">
            &lt;
          </button>
          <button
            v-for="page in displayedPages"
            :key="page"
            class="page-btn page-num"
            :class="{ active: page === currentPage }"
            @click="currentPage = page"
          >
            {{ page }}
          </button>
          <button class="page-btn page-nav" :disabled="currentPage === totalPages" @click="currentPage++">
            &gt;
          </button>
          <select class="page-select" v-model="pageSize">
            <option value="10">10 条 / 页</option>
            <option value="20">20 条 / 页</option>
            <option value="50">50 条 / 页</option>
          </select>
          <div class="page-jump">
            <span>跳至</span>
            <input type="number" class="page-input" v-model="jumpPage" min="1" :max="totalPages" />
            <span>页</span>
            <button class="page-btn page-go" @click="handleJump">Go</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, watch } from 'vue'
import { sparePartsUsageService, SparePartsUsage } from '../services/sparePartsUsage'
import SearchInput from '../components/SearchInput.vue'

export default defineComponent({
  name: 'SparePartsManagement',
  components: {
    SearchInput
  },
  setup() {
    const currentPage = ref(1)
    const pageSize = ref(10)
    const jumpPage = ref(1)
    const loading = ref(false)
    const totalElements = ref(0)
    const totalPages = ref(1)

    const searchForm = ref({
      personnel: '',
      productName: '',
      projectName: ''
    })

    const personnelList = ref<string[]>([])
    const projectList = ref<string[]>([])
    const partsData = ref<SparePartsUsage[]>([])

    const displayedPages = computed(() => {
      const pages: number[] = []
      const start = Math.max(1, currentPage.value - 2)
      const end = Math.min(totalPages.value, currentPage.value + 2)
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    })

    const formatDate = (dateStr: string) => {
      if (!dateStr) return '-'
      try {
        const date = new Date(dateStr)
        return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
      } catch {
        return dateStr
      }
    }

    const loadData = async () => {
      loading.value = true
      try {
        const response = await sparePartsUsageService.getList({
          page: currentPage.value - 1,
          pageSize: Number(pageSize.value),
          user: searchForm.value.personnel || undefined,
          product: searchForm.value.productName || undefined,
          project: searchForm.value.projectName || undefined
        })

        if (response.code === 200 && response.data) {
          partsData.value = response.data.items || []
          totalElements.value = response.data.total || 0
          totalPages.value = Math.ceil(totalElements.value / Number(pageSize.value)) || 1
          
          const personnelSet = new Set<string>()
          const projectSet = new Set<string>()
          partsData.value.forEach(item => {
            if (item.userName) personnelSet.add(item.userName)
            if (item.projectName) projectSet.add(item.projectName)
          })
          personnelList.value = Array.from(personnelSet)
          projectList.value = Array.from(projectSet)
        }
      } catch (error) {
        console.error('加载备品备件领用数据失败:', error)
        partsData.value = []
        totalElements.value = 0
        totalPages.value = 1
      } finally {
        loading.value = false
      }
    }

    const handleSearch = () => {
      currentPage.value = 1
      loadData()
    }

    const handleJump = () => {
      const page = parseInt(String(jumpPage.value))
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
      }
    }

    watch([currentPage, pageSize], () => {
      loadData()
    })

    onMounted(() => {
      loadData()
    })

    return {
      currentPage,
      pageSize,
      jumpPage,
      loading,
      totalElements,
      totalPages,
      searchForm,
      personnelList,
      projectList,
      partsData,
      displayedPages,
      formatDate,
      handleSearch,
      handleJump
    }
  }
})
</script>

<style scoped>
.spare-parts-page {
  background: #fff;
  min-height: 100vh;
}

.content {
  padding: 20px;
}

.search-section {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  align-items: center;
}

.search-form {
  display: flex;
  gap: 16px;
  align-items: center;
  flex: 1;
}

.search-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  white-space: nowrap;
}

.search-input {
  padding: 8px 12px;
  border: 1px solid #d0d7de;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
  min-width: 200px;
}

.search-input:focus {
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.search-select {
  padding: 8px 12px;
  border: 1px solid #d0d7de;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
  min-width: 150px;
  background: #fff;
  cursor: pointer;
}

.search-select:focus {
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-search {
  background: #1976d2;
  color: #fff;
}

.btn-search:hover {
  background: #1565c0;
}

.table-section {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table thead {
  background: #f5f5f5;
}

.data-table th {
  padding: 12px 8px;
  text-align: left;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #e0e0e0;
}

.data-table tbody tr {
  transition: background 0.15s;
}

.data-table tbody tr:hover {
  background: #f9f9f9;
}

.data-table tbody tr.even-row {
  background: #fafafa;
}

.data-table td {
  padding: 12px 8px;
  border-bottom: 1px solid #e0e0e0;
  font-size: 14px;
  color: #666;
}

.pagination-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-top: 1px solid #e0e0e0;
}

.pagination-info {
  font-size: 14px;
  color: #666;
}

.pagination-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}

.page-btn {
  min-width: 32px;
  padding: 6px 12px;
  border: 1px solid #d0d7de;
  border-radius: 4px;
  background: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #f5f5f5;
  border-color: #1976d2;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-btn.page-num {
  min-width: 36px;
}

.page-btn.active {
  background: #1976d2;
  color: #fff;
  border-color: #1976d2;
}

.page-select {
  padding: 6px 8px;
  border: 1px solid #d0d7de;
  border-radius: 4px;
  font-size: 14px;
  background: #fff;
  cursor: pointer;
  outline: none;
}

.page-select:focus {
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.page-jump {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
}

.page-input {
  width: 60px;
  padding: 6px 8px;
  border: 1px solid #d0d7de;
  border-radius: 4px;
  font-size: 14px;
  text-align: center;
  outline: none;
}

.page-input:focus {
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.page-btn.page-go {
  background: #1976d2;
  color: #fff;
}

.page-btn.page-go:hover {
  background: #1565c0;
}
</style>
