<template>
  <div class="inspection-item-page">
    <div class="content-body">
      <div class="tree-section">
        <div class="section-header">
          <div class="section-title">
            <span>巡检事项分类</span>
          </div>
          <div class="section-actions">
            <el-button size="small" @click="handleExpandAll">
              全部展开
            </el-button>
            <el-button size="small" @click="handleCollapseAll">
              全部收起
            </el-button>
          </div>
        </div>

        <div class="tree-toolbar">
          <SearchInput
            v-model="filterText"
            field-key="InspectionItemPage_filter"
            placeholder="搜索分类..."
            @input="handleSearchInput"
          />
          
          <div class="toolbar-actions">
            <el-checkbox v-model="showCheckbox" @change="handleCheckboxChange">
              多选模式
            </el-checkbox>
            <el-button 
              v-if="showCheckbox && checkedNodes.length > 0"
              size="small" 
              type="danger"
              @click="handleBatchDelete"
            >
              批量删除 ({{ checkedNodes.length }})
            </el-button>
          </div>
        </div>

        <div class="tree-content" @contextmenu.prevent>
          <div v-if="loading" class="loading-container">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>加载中...</span>
          </div>
          <el-tree
            v-else
            ref="treeRef"
            :data="treeData"
            :props="defaultProps"
            :filter-node-method="filterNode"
            :highlight-current="true"
            :expand-on-click-node="false"
            :check-on-click-node="showCheckbox"
            :show-checkbox="showCheckbox"
            :check-strictly="false"
            :draggable="true"
            :allow-drop="allowDrop"
            :allow-drag="allowDrag"
            node-key="id"
            :indent="24"
            @node-click="handleNodeClick"
            @node-contextmenu="handleContextMenu"
            @check="handleCheck"
            @node-drop="handleDrop"
          >
            <template #default="{ node, data }">
              <div class="custom-tree-node">
                <div class="node-content">
                  <el-icon class="node-icon" :class="`level-${data.level}`">
                    <component :is="getNodeIcon(data.level)" />
                  </el-icon>
                  <span class="node-label" :title="node.label">{{ node.label }}</span>
                  <el-tag 
                    v-if="data.level === 3 && data.check_content" 
                    size="small" 
                    type="success"
                    class="node-tag"
                  >
                    已配置
                  </el-tag>
                </div>
                <div class="node-actions" @click.stop>
                  <el-button
                    v-if="data.level < 3"
                    type="primary"
                    size="small"
                    text
                    @click.stop="handleAdd(data)"
                  >
                    新增
                  </el-button>
                  <el-button
                    type="primary"
                    size="small"
                    text
                    @click.stop="handleEdit(data)"
                  >
                    编辑
                  </el-button>
                  <el-button
                    v-if="data.level !== 1"
                    type="danger"
                    size="small"
                    text
                    @click.stop="handleDelete(data)"
                  >
                    删除
                  </el-button>
                </div>
              </div>
            </template>
          </el-tree>
        </div>

        <div
          v-if="contextMenuVisible"
          class="context-menu"
          :style="{ top: contextMenuY + 'px', left: contextMenuX + 'px' }"
          @click.stop
        >
          <div class="context-menu-item" @click="handleAddFromMenu">
            新增子节点
          </div>
          <div class="context-menu-item" @click="handleAddSiblingFromMenu">
            新增同级节点
          </div>
          <div class="context-menu-item" @click="handleEditFromMenu">
            重命名
          </div>
          <div class="context-menu-item" v-if="contextMenuNode && contextMenuNode.level !== 1" @click="handleDeleteFromMenu">
            删除节点
          </div>
        </div>
      </div>

      <div class="divider"></div>

      <div class="form-section">
        <template v-if="selectedNode && selectedNode.level === 3">
          <div class="form-header">
            <div class="form-title">
              <span>详细检查要求</span>
            </div>
            <div class="form-subtitle">
              当前选中：{{ selectedNode.item_name }}
            </div>
          </div>
          
          <div class="form-content">
            <el-form :model="formData" label-position="top">
              <el-form-item label="检查内容">
                <el-input
                  v-model="formData.check_content"
                  type="textarea"
                  :rows="5"
                  placeholder="请输入检查内容..."
                  maxlength="1000"
                  show-word-limit
                />
              </el-form-item>
              <el-form-item label="检查标准">
                <el-input
                  v-model="formData.check_standard"
                  type="textarea"
                  :rows="5"
                  placeholder="请输入检查标准..."
                  maxlength="1000"
                  show-word-limit
                />
              </el-form-item>
            </el-form>
          </div>

          <div class="form-actions">
            <el-button @click="handleCancel">取消</el-button>
            <el-button type="primary" @click="handleSave" :loading="saving">
              保存
            </el-button>
          </div>
        </template>
        
        <template v-else>
          <div class="empty-state">
            <el-empty description="请选择三级检查项进行编辑">
              <template #image>
                <el-icon :size="64" color="#dcdfe6"><Document /></el-icon>
              </template>
            </el-empty>
            <div class="empty-hint">
              <el-alert
                title="提示"
                type="info"
                :closable="false"
              >
                一、二级节点仅作为分类使用，无法编辑检查要求
              </el-alert>
            </div>
          </div>
        </template>
      </div>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="400px"
      @close="handleDialogClose"
    >
      <el-form :model="dialogForm" label-width="80px">
        <el-form-item label="节点名称">
          <el-input
            v-model="dialogForm.item_name"
            placeholder="请输入节点名称"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="事项类型">
          <el-input
            v-model="dialogForm.item_type"
            placeholder="请输入事项类型"
            maxlength="50"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleDialogConfirm" :loading="dialogLoading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, watch, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { ElTree } from 'element-plus'
import type Node from 'element-plus/es/components/tree/src/model/node'
import { inspectionItemService, type InspectionItem } from '@/services/inspectionItem'
import SearchInput from '@/components/SearchInput.vue'

interface TreeNodeData extends InspectionItem {
  label: string
  children?: TreeNodeData[]
}

interface TreeProps {
  label: string
  children?: string
  disabled?: boolean
  isLeaf?: boolean
}

const treeRef = ref<InstanceType<typeof ElTree>>()
const filterText = ref('')
const showCheckbox = ref(false)
const checkedNodes = ref<TreeNodeData[]>([])
const selectedNode = ref<TreeNodeData | null>(null)
const saving = ref(false)
const loading = ref(false)

const contextMenuVisible = ref(false)
const contextMenuX = ref(0)
const contextMenuY = ref(0)
const contextMenuNode = ref<TreeNodeData | null>(null)

const dialogVisible = ref(false)
const dialogTitle = ref('')
const dialogLoading = ref(false)
const dialogForm = reactive({
  item_name: '',
  item_type: '',
  type: '' as '' | 'add' | 'edit' | 'addSibling',
  parentNode: null as TreeNodeData | null,
  currentNode: null as TreeNodeData | null
})

const formData = reactive({
  check_content: '',
  check_standard: ''
})

const defaultProps: TreeProps = {
  label: 'label',
  children: 'children'
}

const treeData = ref<TreeNodeData[]>([])

const loadTreeData = async () => {
  loading.value = true
  try {
    const response = await inspectionItemService.getTree()
    if (response.code === 200 && response.data) {
      treeData.value = transformToTreeData(response.data)
    }
  } catch (error) {
    console.error('加载巡检事项树失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const transformToTreeData = (items: InspectionItem[]): TreeNodeData[] => {
  return items.map(item => ({
    ...item,
    label: item.item_name,
    children: item.children ? transformToTreeData(item.children) : []
  }))
}

watch(filterText, (val) => {
  treeRef.value?.filter(val)
})

const getNodeIcon = (level: number) => {
  const icons: Record<number, string> = {
    1: 'FolderOpened',
    2: 'Folder',
    3: 'Document'
  }
  return icons[level] || 'Document'
}

const filterNode = (value: string, data: TreeNodeData) => {
  if (!value) return true
  return data.label.toLowerCase().includes(value.toLowerCase())
}

const handleSearchClear = () => {
  filterText.value = ''
}

const handleSearchInput = (value: string) => {
  filterText.value = value
  treeRef.value?.filter(value)
}

const handleExpandAll = () => {
  const nodes = treeRef.value?.store?.nodesMap
  if (nodes) {
    Object.values(nodes).forEach((node: any) => {
      node.expanded = true
    })
  }
}

const handleCollapseAll = () => {
  const nodes = treeRef.value?.store?.nodesMap
  if (nodes) {
    Object.values(nodes).forEach((node: any) => {
      node.expanded = false
    })
  }
}

const handleCheckboxChange = (val: boolean) => {
  if (!val) {
    checkedNodes.value = []
    treeRef.value?.setCheckedKeys([])
  }
}

const handleCheck = (data: TreeNodeData, { checkedNodes: nodes }: any) => {
  checkedNodes.value = nodes
}

const handleNodeClick = (data: TreeNodeData, node: Node) => {
  selectedNode.value = data
  if (data.level === 3) {
    formData.check_content = data.check_content || ''
    formData.check_standard = data.check_standard || ''
  }
}

const handleContextMenu = (e: MouseEvent, data: TreeNodeData, node: Node, element: any) => {
  e.preventDefault()
  contextMenuNode.value = data
  contextMenuX.value = e.clientX
  contextMenuY.value = e.clientY
  contextMenuVisible.value = true
}

const closeContextMenu = () => {
  contextMenuVisible.value = false
}

const handleAdd = (data: TreeNodeData) => {
  dialogTitle.value = '新增子节点'
  dialogForm.type = 'add'
  dialogForm.parentNode = data
  dialogForm.currentNode = null
  dialogForm.item_name = ''
  dialogForm.item_type = data.item_type
  dialogVisible.value = true
}

const handleAddFromMenu = () => {
  if (contextMenuNode.value) {
    handleAdd(contextMenuNode.value)
  }
  closeContextMenu()
}

const handleAddSibling = (data: TreeNodeData) => {
  dialogTitle.value = '新增同级节点'
  dialogForm.type = 'addSibling'
  dialogForm.parentNode = null
  dialogForm.currentNode = data
  dialogForm.item_name = ''
  dialogForm.item_type = data.item_type
  dialogVisible.value = true
}

const handleAddSiblingFromMenu = () => {
  if (contextMenuNode.value) {
    handleAddSibling(contextMenuNode.value)
  }
  closeContextMenu()
}

const handleEdit = (data: TreeNodeData) => {
  dialogTitle.value = '编辑节点'
  dialogForm.type = 'edit'
  dialogForm.parentNode = null
  dialogForm.currentNode = data
  dialogForm.item_name = data.item_name
  dialogForm.item_type = data.item_type
  dialogVisible.value = true
}

const handleEditFromMenu = () => {
  if (contextMenuNode.value) {
    handleEdit(contextMenuNode.value)
  }
  closeContextMenu()
}

const handleDelete = async (data: TreeNodeData) => {
  const hasChildren = data.children && data.children.length > 0
  const message = hasChildren 
    ? '删除该节点将同时删除所有子节点，确定要删除吗？' 
    : '确定要删除该节点吗？'
  
  try {
    await ElMessageBox.confirm(message, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await inspectionItemService.delete(data.id)
    ElMessage.success('删除成功')
    await loadTreeData()
    
    if (selectedNode.value?.id === data.id) {
      selectedNode.value = null
      formData.check_content = ''
      formData.check_standard = ''
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const handleDeleteFromMenu = () => {
  if (contextMenuNode.value) {
    handleDelete(contextMenuNode.value)
  }
  closeContextMenu()
}

const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${checkedNodes.value.length} 个节点吗？`,
      '批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    for (const node of checkedNodes.value) {
      if (node.level !== 1) {
        await inspectionItemService.delete(node.id)
      }
    }
    
    checkedNodes.value = []
    treeRef.value?.setCheckedKeys([])
    ElMessage.success('批量删除成功')
    await loadTreeData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '批量删除失败')
    }
  }
}

const handleDialogClose = () => {
  dialogForm.item_name = ''
  dialogForm.item_type = ''
  dialogForm.type = ''
  dialogForm.parentNode = null
  dialogForm.currentNode = null
}

const handleDialogConfirm = async () => {
  if (!dialogForm.item_name.trim()) {
    ElMessage.warning('请输入节点名称')
    return
  }
  
  dialogLoading.value = true
  try {
    if (dialogForm.type === 'add' && dialogForm.parentNode) {
      const newItem = {
        item_code: `ITEM-${Date.now()}`,
        item_name: dialogForm.item_name.trim(),
        item_type: dialogForm.item_type || dialogForm.parentNode.item_type,
        level: dialogForm.parentNode.level + 1,
        parent_id: dialogForm.parentNode.id
      }
      await inspectionItemService.create(newItem)
      ElMessage.success('新增成功')
    } else if (dialogForm.type === 'addSibling' && dialogForm.currentNode) {
      const newItem = {
        item_code: `ITEM-${Date.now()}`,
        item_name: dialogForm.item_name.trim(),
        item_type: dialogForm.item_type || dialogForm.currentNode.item_type,
        level: dialogForm.currentNode.level,
        parent_id: dialogForm.currentNode.parent_id
      }
      await inspectionItemService.create(newItem)
      ElMessage.success('新增同级节点成功')
    } else if (dialogForm.type === 'edit' && dialogForm.currentNode) {
      await inspectionItemService.update(dialogForm.currentNode.id, {
        item_name: dialogForm.item_name.trim(),
        item_type: dialogForm.item_type
      })
      ElMessage.success('编辑成功')
    }
    
    dialogVisible.value = false
    await loadTreeData()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    dialogLoading.value = false
  }
}

const handleCancel = () => {
  if (selectedNode.value) {
    selectedNode.value = null
    formData.check_content = ''
    formData.check_standard = ''
  }
}

const handleSave = async () => {
  if (!selectedNode.value) return
  
  saving.value = true
  try {
    await inspectionItemService.update(selectedNode.value.id, {
      check_content: formData.check_content,
      check_standard: formData.check_standard
    })
    selectedNode.value.check_content = formData.check_content
    selectedNode.value.check_standard = formData.check_standard
    ElMessage.success('保存成功')
    await loadTreeData()
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

const allowDrop = (draggingNode: Node, dropNode: Node, type: 'prev' | 'inner' | 'next') => {
  if (type === 'inner') {
    return dropNode.data.level < 3
  }
  return true
}

const allowDrag = (draggingNode: Node) => {
  return draggingNode.data.level !== 1
}

const handleDrop = async (draggingNode: Node, dropNode: Node, dropType: string, ev: DragEvent) => {
  const draggingData = draggingNode.data as TreeNodeData
  const dropData = dropNode.data as TreeNodeData
  
  let newParentId: number | null = null
  
  if (dropType === 'inner') {
    newParentId = dropData.id
  } else {
    newParentId = dropData.parent_id
  }
  
  try {
    await inspectionItemService.update(draggingData.id, {
      parent_id: newParentId
    })
    ElMessage.success(`节点已移动`)
  } catch (error) {
    ElMessage.error('移动失败')
    await loadTreeData()
  }
}

onMounted(() => {
  document.addEventListener('click', closeContextMenu)
  loadTreeData()
  window.addEventListener('user-changed', handleUserChanged)
})

onUnmounted(() => {
  document.removeEventListener('click', closeContextMenu)
  window.removeEventListener('user-changed', handleUserChanged)
})

const handleUserChanged = () => {
  loadTreeData()
}
</script>

<style scoped>
.inspection-item-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
}

.content-body {
  display: flex;
  gap: 0;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  min-height: calc(100vh - 160px);
}

.tree-section {
  width: 320px;
  min-width: 320px;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-right: 1px solid #dcdfe6;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
  background: #fafafa;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.section-actions {
  display: flex;
  gap: 8px;
}

.tree-toolbar {
  padding: 16px;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.toolbar-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tree-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 8px;
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  gap: 8px;
  color: #909399;
}

.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  padding-right: 8px;
}

.node-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.node-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.node-icon.level-1 {
  color: #409eff;
}

.node-icon.level-2 {
  color: #67c23a;
}

.node-icon.level-3 {
  color: #909399;
}

.node-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.node-tag {
  margin-left: 8px;
  flex-shrink: 0;
}

.node-actions {
  display: none;
  gap: 4px;
}

.custom-tree-node:hover .node-actions {
  display: flex;
}

.context-menu {
  position: fixed;
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  padding: 4px 0;
  min-width: 140px;
}

.context-menu-item {
  padding: 8px 16px;
  font-size: 14px;
  color: #606266;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.context-menu-item:hover {
  background: #f5f7fa;
  color: #409eff;
}

.divider {
  width: 1px;
  background: #dcdfe6;
  flex-shrink: 0;
}

.form-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fafafa;
  min-width: 0;
}

.form-header {
  padding: 20px 32px 16px;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
}

.form-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.form-subtitle {
  font-size: 13px;
  color: #909399;
  padding-left: 24px;
}

.form-content {
  flex: 1;
  padding: 20px 32px;
  overflow-y: auto;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 32px;
  background: #fff;
  border-top: 1px solid #ebeef5;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.empty-hint {
  margin-top: 20px;
  max-width: 400px;
}
</style>
