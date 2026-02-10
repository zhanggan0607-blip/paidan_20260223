<template>
  <div class="inspection-item-page">
    <div class="breadcrumb-section">
      <div class="breadcrumb">
        <span class="breadcrumb-item">系统管理</span>
        <span class="breadcrumb-separator">/</span>
        <span class="breadcrumb-item active">巡检事项管理</span>
      </div>
    </div>

    <div class="content-body">
      <div class="tree-section">
        <div class="tree-search-wrapper">
          <div class="tree-search-box">
            <span class="search-icon">🔍</span>
            <input
              type="text"
              class="search-input"
              placeholder="请输入内容"
              v-model="searchKeyword"
              @input="handleSearch"
            />
            <span v-if="searchKeyword" class="clear-icon" @click="clearSearch">×</span>
          </div>
        </div>
        <div class="tree-content" ref="treeContainer" @click="closeContextMenu">
          <TreeNode
            v-for="node in treeData"
            :key="node.id"
            :node="node"
            :searchKeyword="searchKeyword"
            :depth="0"
            @select="handleNodeSelect"
            @toggle="handleNodeToggle"
            @drag="handleNodeDrag"
            @add="handleAddNode"
            @delete="handleDeleteNode"
            @rename="handleRenameNode"
            @contextmenu="handleContextMenu"
          />
        </div>
        <div
          v-if="contextMenuVisible()"
          class="context-menu"
          :style="{ top: contextMenuY + 'px', left: contextMenuX + 'px' }"
          @click.stop
        >
          <div class="context-menu-item" @click="handleAddFromMenu">新增子节点</div>
          <div class="context-menu-item" @click="handleRenameFromMenu">重命名</div>
          <div class="context-menu-item context-menu-delete" @click="handleDeleteFromMenu" v-if="!isRootNode">删除节点</div>
        </div>
      </div>

      <div class="divider"></div>

      <div class="form-section">
        <template v-if="selectedNode && selectedNode.level >= 3">
          <div class="form-title-row">
            <span class="form-title">详细检查要求</span>
            <span class="form-hint">（最多1000字符）</span>
          </div>
          <div class="textarea-wrapper" :class="{ 'textarea-error': isOverLimit }">
            <textarea
              class="form-textarea"
              placeholder="请输入多行文本"
              v-model="checkRequirement"
              @input="handleTextareaInput"
              @keydown="handleTextareaKeydown"
            ></textarea>
            <div class="char-count" :class="{ 'char-count-error': isOverLimit }">
              {{ checkRequirement.length }}字 / 1000字
            </div>
          </div>
          <div class="form-actions">
            <button
              class="btn btn-save"
              @click="handleSave"
              :disabled="isSaveDisabled || isOverLimit"
            >
              保存
            </button>
          </div>
          <div v-if="saveSuccess" class="save-success-toast">
            ✓ 保存成功
          </div>
          <div v-if="showEmptyAlert" class="save-error-toast">
            ⚠ 请输入检查要求
          </div>
        </template>
        <template v-else>
          <div class="no-selection-tip">请选择三级及以上节点</div>
        </template>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'

interface TreeNodeData {
  id: string
  label: string
  level: number
  expanded?: boolean
  selected?: boolean
  matched?: boolean
  checkRequirement?: string
  children?: TreeNodeData[]
}

interface ContextMenuData {
  visible: boolean
  x: number
  y: number
  node: TreeNodeData | null
}

const TreeNode = defineComponent({
  name: 'TreeNode',
  props: {
    node: {
      type: Object as () => TreeNodeData,
      required: true
    },
    searchKeyword: {
      type: String,
      default: ''
    },
    depth: {
      type: Number,
      default: 0
    }
  },
  emits: ['select', 'toggle', 'drag', 'add', 'delete', 'rename', 'contextmenu'],
  setup(props: { node: TreeNodeData; searchKeyword: string; depth: number }, { emit }) {
    const hasChildren = computed(() => props.node.children && props.node.children.length > 0)
    const isLeaf = computed(() => !hasChildren.value)
    const showChildren = computed(() => props.node.expanded && hasChildren.value)
    const indentWidth = computed(() => {
      if (props.depth === 0) return 0
      if (props.depth === 1) return 24
      return 24 + (props.depth - 1) * 24
    })

    const handleSelect = (e: MouseEvent) => {
      e.stopPropagation()
      emit('select', props.node)
    }

    const handleToggle = (e: MouseEvent) => {
      e.stopPropagation()
      emit('toggle', props.node)
    }

    const handleDragStart = (e: DragEvent) => {
      if (e.dataTransfer) {
        e.dataTransfer.setData('nodeId', props.node.id)
        e.dataTransfer.effectAllowed = 'move'
      }
    }

    const handleDragOver = (e: DragEvent) => {
      e.preventDefault()
      if (e.dataTransfer) {
        e.dataTransfer.dropEffect = 'move'
      }
    }

    const handleDrop = (e: DragEvent) => {
      e.preventDefault()
      e.stopPropagation()
      const draggedId = e.dataTransfer?.getData('nodeId')
      if (draggedId && draggedId !== props.node.id) {
        emit('drag', draggedId, props.node.id)
      }
    }

    const handleContextMenu = (e: MouseEvent) => {
      e.preventDefault()
      e.stopPropagation()
      emit('contextmenu', props.node, e)
    }

    return {
      hasChildren,
      isLeaf,
      showChildren,
      indentWidth,
      handleSelect,
      handleToggle,
      handleDragStart,
      handleDragOver,
      handleDrop,
      handleContextMenu
    }
  },
  template: `
    <div class="tree-node-wrapper">
      <div
        class="node-content"
        :class="{
          'node-selected': node.selected,
          'node-matched': node.matched,
          'node-level-0': depth === 0,
          'node-level-1': depth === 1,
          'node-level-2': depth >= 2
        }"
        :draggable="true"
        :style="{ paddingLeft: indentWidth + 'px' }"
        @click="handleSelect"
        @dragstart="handleDragStart"
        @dragover="handleDragOver"
        @drop="handleDrop"
        @contextmenu="handleContextMenu"
      >
        <span class="node-connector" v-if="depth >= 1">
          <span class="connector-line"></span>
        </span>
        <span
          class="node-toggle"
          :class="{ 'has-children': hasChildren }"
          @click.stop="handleToggle"
          v-if="hasChildren"
        >
          {{ node.expanded ? '▼' : '▶' }}
        </span>
        <span class="node-toggle node-no-children" v-else>·</span>
        <span class="node-label">{{ node.label }}</span>
      </div>
      <div v-if="showChildren" class="node-children">
        <TreeNode
          v-for="child in node.children"
          :key="child.id"
          :node="child"
          :searchKeyword="searchKeyword"
          :depth="depth + 1"
          @select="$emit('select', $event)"
          @toggle="$emit('toggle', $event)"
          @drag="$emit('drag', $event)"
          @add="$emit('add', $event)"
          @delete="$emit('delete', $event)"
          @rename="$emit('rename', $event)"
          @contextmenu="$emit('contextmenu', $event)"
        />
      </div>
    </div>
  `
})

export default defineComponent({
  name: 'InspectionItemPage',
  components: { TreeNode },
  setup() {
    const searchKeyword = ref('')
    const selectedNode = ref<TreeNodeData | null>(null)
    const checkRequirement = ref('')
    const treeContainer = ref<HTMLElement | null>(null)
    const saveSuccess = ref(false)
    const showEmptyAlert = ref(false)
    const isOverLimit = ref(false)
    const contextMenu = reactive<ContextMenuData>({
      visible: false,
      x: 0,
      y: 0,
      node: null
    })

    const treeData = reactive<TreeNodeData[]>([
      {
        id: '1',
        label: '弱电项目',
        level: 1,
        expanded: true,
        children: [
          {
            id: '1-1',
            label: '门禁系统',
            level: 2,
            expanded: false,
            children: []
          },
          {
            id: '1-2',
            label: '综合布线系统',
            level: 2,
            expanded: true,
            children: [
              {
                id: '1-2-1',
                label: '云台摄像头',
                level: 3,
                expanded: true,
                checkRequirement: '',
                children: [
                  {
                    id: '1-2-1-1',
                    label: '机房内环境检查',
                    level: 4,
                    checkRequirement: '检查机房温度、湿度、洁净度是否在规定范围内',
                    children: []
                  }
                ]
              }
            ]
          },
          {
            id: '1-3',
            label: 'XXX项目',
            level: 2,
            expanded: false,
            children: []
          },
          {
            id: '1-4',
            label: 'A医院菜单3',
            level: 2,
            expanded: false,
            children: []
          },
          {
            id: '1-5',
            label: 'A医院菜单4',
            level: 2,
            expanded: false,
            children: []
          },
          {
            id: '1-6',
            label: 'A医院菜单5',
            level: 2,
            expanded: false,
            children: []
          },
          {
            id: '1-7',
            label: 'A医院菜单6',
            level: 2,
            expanded: false,
            children: []
          }
        ]
      }
    ])

    const isRootNode = computed(() => contextMenu.node?.level === 1)
    const isSaveDisabled = computed(() => !selectedNode.value || selectedNode.value.level < 3)

    const clearSearch = () => {
      searchKeyword.value = ''
      clearMatchedState(treeData)
    }

    const clearMatchedState = (nodes: TreeNodeData[]) => {
      for (const node of nodes) {
        node.matched = false
        if (node.children && node.children.length > 0) {
          clearMatchedState(node.children)
        }
      }
    }

    const findNodeById = (nodes: TreeNodeData[], id: string): TreeNodeData | null => {
      for (const node of nodes) {
        if (node.id === id) return node
        if (node.children && node.children.length > 0) {
          const found = findNodeById(node.children, id)
          if (found) return found
        }
      }
      return null
    }

    const clearSelection = (nodes: TreeNodeData[]) => {
      for (const node of nodes) {
        node.selected = false
        if (node.children && node.children.length > 0) {
          clearSelection(node.children)
        }
      }
    }

    const expandToPath = (nodes: TreeNodeData[], targetId: string): boolean => {
      for (const node of nodes) {
        if (node.id === targetId) {
          return true
        }
        if (node.children?.some(child => child.id.startsWith(node.id))) {
          node.expanded = true
          if (node.children) {
            expandToPath(node.children, targetId)
          }
          return true
        }
      }
      return false
    }

    const setMatchedState = (nodes: TreeNodeData[], keyword: string): boolean => {
      let hasMatch = false
      for (const node of nodes) {
        const nodeMatch = node.label.toLowerCase().includes(keyword.toLowerCase())
        const childMatch = node.children ? setMatchedState(node.children, keyword) : false

        if (nodeMatch || childMatch) {
          node.matched = true
          hasMatch = true
          if (node.children) {
            for (const child of node.children) {
              if (child.matched) {
                node.expanded = true
                break
              }
            }
          }
        } else {
          node.matched = false
        }
      }
      return hasMatch
    }

    const handleSearch = () => {
      if (searchKeyword.value.length < 2) {
        clearMatchedState(treeData)
        return
      }

      const keyword = searchKeyword.value.toLowerCase()
      setMatchedState(treeData, keyword)

      for (const node of treeData) {
        if (node.matched) {
          expandToPath(treeData, node.id)
        }
      }
    }

    const handleNodeSelect = (node: TreeNodeData) => {
      clearSelection(treeData)
      node.selected = true
      selectedNode.value = node
      checkRequirement.value = node.checkRequirement || ''
    }

    const handleNodeToggle = (node: TreeNodeData) => {
      node.expanded = !node.expanded
    }

    const findAndRemoveNode = (nodes: TreeNodeData[], id: string): TreeNodeData | null => {
      for (let i = 0; i < nodes.length; i++) {
        if (nodes[i].id === id) {
          return nodes.splice(i, 1)[0]
        }
        if (nodes[i].children?.length) {
          const found = findAndRemoveNode(nodes[i].children!, id)
          if (found) return found
        }
      }
      return null
    }

    const insertNodeAfter = (nodes: TreeNodeData[], targetId: string, newNode: TreeNodeData): boolean => {
      for (let i = 0; i < nodes.length; i++) {
        if (nodes[i].id === targetId) {
          nodes.splice(i + 1, 0, newNode)
          return true
        }
        if (nodes[i].children?.length) {
          const found = insertNodeAfter(nodes[i].children!, targetId, newNode)
          if (found) return true
        }
      }
      return false
    }

    const handleNodeDrag = (draggedId: string, targetId: string) => {
      const draggedNode = findAndRemoveNode(treeData, draggedId)
      if (draggedNode) {
        const targetNode = findNodeById(treeData, targetId)
        if (targetNode && draggedNode.level === targetNode.level) {
          insertNodeAfter(treeData, targetId, draggedNode)
        }
      }
    }

    const generateId = () => `node-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

    const handleAddNode = (parentNode: TreeNodeData) => {
      if (!parentNode.children) {
        parentNode.children = []
      }
      parentNode.expanded = true

      const newNode: TreeNodeData = {
        id: generateId(),
        label: '新节点',
        level: parentNode.level + 1,
        checkRequirement: '',
        expanded: false,
        children: []
      }

      parentNode.children.push(newNode)
    }

    const handleDeleteNode = (node: TreeNodeData) => {
      if (node.level === 1) return
      if (node.children && node.children.length > 0) {
        if (!confirm('删除该节点将同时删除所有子节点，确定要删除吗？')) return
      }
      const removed = findAndRemoveNode(treeData, node.id)
      if (removed && selectedNode.value?.id === node.id) {
        selectedNode.value = null
        checkRequirement.value = ''
      }
    }

    const handleRenameNode = (node: TreeNodeData) => {
      const newLabel = prompt('请输入新名称：', node.label)
      if (newLabel && newLabel.trim()) {
        node.label = newLabel.trim()
      }
    }

    const handleContextMenu = (node: TreeNodeData, e: MouseEvent) => {
      contextMenu.node = node
      contextMenu.x = e.clientX
      contextMenu.y = e.clientY
      contextMenu.visible = true
    }

    const closeContextMenu = () => {
      contextMenu.visible = false
    }

    const handleAddFromMenu = () => {
      if (contextMenu.node) {
        handleAddNode(contextMenu.node)
      }
      closeContextMenu()
    }

    const handleRenameFromMenu = () => {
      if (contextMenu.node) {
        handleRenameNode(contextMenu.node)
      }
      closeContextMenu()
    }

    const handleDeleteFromMenu = () => {
      if (contextMenu.node) {
        handleDeleteNode(contextMenu.node)
      }
      closeContextMenu()
    }

    const handleTextareaInput = () => {
      if (checkRequirement.value.length > 1000) {
        checkRequirement.value = checkRequirement.value.substring(0, 1000)
      }
      isOverLimit.value = checkRequirement.value.length > 1000
    }

    const handleTextareaKeydown = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        e.preventDefault()
        const textarea = e.target as HTMLTextAreaElement
        const start = textarea.selectionStart
        const end = textarea.selectionEnd
        textarea.value = textarea.value.substring(0, start) + '  ' + textarea.value.substring(end)
        textarea.selectionStart = textarea.selectionEnd = start + 2
      }
    }

    const handleSave = () => {
      if (!checkRequirement.value.trim()) {
        showEmptyAlert.value = true
        setTimeout(() => {
          showEmptyAlert.value = false
        }, 3000)
        return
      }

      if (selectedNode.value) {
        selectedNode.value.checkRequirement = checkRequirement.value
        saveSuccess.value = true
        setTimeout(() => {
          saveSuccess.value = false
        }, 3000)
      }
    }

    const handleGlobalKeydown = (e: KeyboardEvent) => {
      if (e.ctrlKey) {
        if (e.key === 'a' || e.key === 'A') {
          e.preventDefault()
          const allNodes: TreeNodeData[] = []
          const collectNodes = (nodes: TreeNodeData[]) => {
            for (const node of nodes) {
              allNodes.push(node)
              if (node.children) collectNodes(node.children)
            }
          }
          collectNodes(treeData)
          clearSelection(treeData)
          if (allNodes.length > 0) {
            allNodes[0].selected = true
            selectedNode.value = allNodes[0]
            checkRequirement.value = allNodes[0].checkRequirement || ''
          }
        } else if (e.key === '+' || e.key === '=') {
          e.preventDefault()
          const expandAll = (nodes: TreeNodeData[]) => {
            for (const node of nodes) {
              node.expanded = true
              if (node.children) expandAll(node.children)
            }
          }
          expandAll(treeData)
        } else if (e.key === '-' || e.key === '_') {
          e.preventDefault()
          const collapseAll = (nodes: TreeNodeData[]) => {
            for (const node of nodes) {
              node.expanded = false
              if (node.children) collapseAll(node.children)
            }
          }
          collapseAll(treeData)
        }
      }
    }

    onMounted(() => {
      document.addEventListener('click', closeContextMenu)
      document.addEventListener('keydown', handleGlobalKeydown)
    })

    onUnmounted(() => {
      document.removeEventListener('click', closeContextMenu)
      document.removeEventListener('keydown', handleGlobalKeydown)
    })

    return {
      searchKeyword,
      selectedNode,
      checkRequirement,
      treeData,
      treeContainer,
      saveSuccess,
      showEmptyAlert,
      isOverLimit,
      isRootNode,
      isSaveDisabled,
      contextMenuVisible: () => contextMenu.visible,
      contextMenuX: () => contextMenu.x,
      contextMenuY: () => contextMenu.y,
      clearSearch,
      handleSearch,
      handleNodeSelect,
      handleNodeToggle,
      handleNodeDrag,
      handleAddNode,
      handleDeleteNode,
      handleRenameNode,
      handleContextMenu,
      closeContextMenu,
      handleAddFromMenu,
      handleRenameFromMenu,
      handleDeleteFromMenu,
      handleTextareaInput,
      handleTextareaKeydown,
      handleSave
    }
  }
})
</script>

<style scoped>
.inspection-item-page {
  min-height: 100vh;
  background: #f8f9fa;
  padding: 20px;
}

.breadcrumb-section {
  margin-bottom: 20px;
  padding: 12px 20px;
  background: #F5F7FA;
  border-radius: 4px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.breadcrumb-item {
  color: #666;
}

.breadcrumb-item.active {
  color: #333;
  font-weight: 500;
}

.breadcrumb-separator {
  color: #999;
}

.content-body {
  display: flex;
  gap: 0;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 0;
  min-height: calc(100vh - 160px);
}

.tree-section {
  width: 60%;
  height: calc(100vh - 200px);
  display: flex;
  flex-direction: column;
  background: #fff;
}

.tree-search-wrapper {
  padding: 16px 16px 0 16px;
  flex-shrink: 0;
}

.tree-search-box {
  width: 100%;
  height: 40px;
  border: 1px solid #D9D9D9;
  border-radius: 4px;
  display: flex;
  align-items: center;
  padding: 0 12px;
  box-sizing: border-box;
  transition: all 0.2s;
}

.tree-search-box:focus-within {
  border-color: #1890FF;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.search-icon {
  font-size: 16px;
  color: #999999;
  margin-right: 8px;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 14px;
  color: #333333;
  background: transparent;
}

.search-input::placeholder {
  color: #999999;
}

.clear-icon {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #999999;
  color: #fff;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.2s;
}

.clear-icon:hover {
  background: #666666;
}

.tree-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 16px;
}

.tree-node-wrapper {
  min-height: 32px;
}

.node-content {
  display: flex;
  align-items: center;
  padding: 6px 8px;
  cursor: pointer;
  border-radius: 3px;
  transition: background 0.15s;
  min-height: 32px;
  box-sizing: border-box;
}

.node-content:hover {
  background: #F5F5F5;
}

.node-content.node-selected {
  background: #E6F7FF;
}

.node-content.node-matched {
  background: #E6F7FF;
}

.node-content.node-selected.node-matched {
  background: #BAE7FF;
}

.node-connector {
  width: 24px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.connector-line {
  width: 1px;
  height: 16px;
  background: #D9D9D9;
}

.node-toggle {
  width: 24px;
  flex-shrink: 0;
  color: #666666;
  font-size: 12px;
  text-align: center;
  user-select: none;
}

.node-toggle.has-children {
  cursor: pointer;
}

.node-toggle.node-no-children {
  color: transparent;
}

.node-label {
  flex: 1;
  font-size: 14px;
  color: #333333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.node-selected .node-label {
  color: #1890FF;
}

.node-children {
  margin-left: 0;
}

.context-menu {
  position: fixed;
  width: 120px;
  background: #fff;
  border: 1px solid #D9D9D9;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  padding: 4px 0;
}

.context-menu-item {
  padding: 8px 16px;
  font-size: 14px;
  color: #333333;
  cursor: pointer;
  transition: background 0.15s;
}

.context-menu-item:hover {
  background: #F5F5F5;
}

.context-menu-delete {
  color: #F5222D;
}

.divider {
  width: 1px;
  background: #E8E8E8;
  margin: 24px 0;
}

.form-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 24px 32px;
  min-width: 0;
  width: 40%;
  box-sizing: border-box;
}

.form-title-row {
  display: flex;
  align-items: baseline;
  margin-bottom: 8px;
}

.form-title {
  font-size: 16px;
  font-weight: bold;
  color: #333333;
}

.form-hint {
  font-size: 12px;
  color: #999999;
  margin-left: 8px;
}

.textarea-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
}

.form-textarea {
  flex: 1;
  width: 100%;
  padding: 12px;
  border: 1px solid #D9D9D9;
  border-radius: 4px;
  font-size: 14px;
  color: #333333;
  background: #fff;
  resize: none;
  font-family: inherit;
  line-height: 1.5;
  transition: all 0.2s;
  box-sizing: border-box;
}

.form-textarea:focus {
  outline: none;
  border-color: #1890FF;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.form-textarea::placeholder {
  color: #999999;
}

.textarea-error .form-textarea {
  border-color: #F5222D;
}

.char-count {
  position: absolute;
  bottom: 8px;
  right: 12px;
  font-size: 12px;
  color: #999999;
  background: #fff;
  padding: 0 4px;
}

.char-count-error {
  color: #F5222D;
}

.no-selection-tip {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: #999999;
}

.form-actions {
  padding-top: 24px;
  display: flex;
  justify-content: center;
}

.btn {
  width: 100px;
  height: 40px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-save {
  background: #1890FF;
  color: #fff;
}

.btn-save:hover:not(:disabled) {
  background: #40A9FF;
}

.btn-save:active:not(:disabled) {
  background: #096DD9;
}

.btn-save:disabled {
  background: #A6CFFF;
  color: #FFFFFF;
  cursor: not-allowed;
}

.save-success-toast {
  position: fixed;
  bottom: 40px;
  right: 40px;
  padding: 12px 20px;
  background: #52C41A;
  color: #fff;
  border-radius: 4px;
  font-size: 14px;
  animation: fadeIn 0.3s ease;
  z-index: 1001;
}

.save-error-toast {
  position: fixed;
  bottom: 40px;
  right: 40px;
  padding: 12px 20px;
  background: #F5222D;
  color: #fff;
  border-radius: 4px;
  font-size: 14px;
  animation: fadeIn 0.3s ease;
  z-index: 1001;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #F5F5F5;
}

::-webkit-scrollbar-thumb {
  background: #CBCBCB;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #A0A0A0;
}
</style>
