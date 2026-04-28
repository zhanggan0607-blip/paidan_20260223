<template>
  <div class="inspection-items-table">
    <div class="section-title">
      {{ title }}（共 {{ items.length }} 条）
    </div>
    <div class="table-section-inner">
      <table class="inner-table">
        <thead>
          <tr>
            <th style="width: 60px">事项编号</th>
            <th>巡查类</th>
            <th>巡查项</th>
            <th>巡查内容</th>
            <th>检查要求</th>
            <th>简要说明</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(item, index) in items"
            :key="index"
          >
            <td>
              <input
                :id="`seq_${index}`"
                :name="`seq_${index}`"
                type="text"
                class="table-input table-input-readonly"
                :value="index + 1"
                readonly
              >
            </td>
            <td>
              <div
                v-if="item.level1_name"
                class="selected-text"
                @click="clearLevel(1, item)"
              >
                {{ item.level1_name }}
              </div>
              <el-select
                v-else
                v-model="item.level1_id"
                placeholder="选择巡查类"
                size="small"
                style="width: 100%"
                @change="handleLevelChange(1, index)"
              >
                <el-option
                  v-for="node in level1Nodes"
                  :key="node.id"
                  :label="node.label"
                  :value="node.id"
                />
              </el-select>
            </td>
            <td>
              <div
                v-if="item.level2_name"
                class="selected-text"
                @click="clearLevel(2, item)"
              >
                {{ item.level2_name }}
              </div>
              <el-select
                v-else
                v-model="item.level2_id"
                placeholder="选择巡查项"
                size="small"
                style="width: 100%"
                :disabled="!item.level1_id"
                @change="handleLevelChange(2, index)"
              >
                <el-option
                  v-for="node in getLevel2Nodes(item.level1_id)"
                  :key="node.id"
                  :label="node.label"
                  :value="node.id"
                />
              </el-select>
            </td>
            <td>
              <div
                v-if="item.level3_name"
                class="selected-text"
                @click="clearLevel(3, item)"
              >
                {{ item.level3_name }}
              </div>
              <el-select
                v-else
                v-model="item.level3_id"
                placeholder="选择巡查内容"
                size="small"
                style="width: 100%"
                :disabled="!item.level2_id"
                @change="handleLevelChange(3, index)"
              >
                <el-option
                  v-for="node in getLevel3Nodes(item.level1_id, item.level2_id)"
                  :key="node.id"
                  :label="node.label"
                  :value="node.id"
                />
              </el-select>
            </td>
            <td>
              <el-input
                v-model="item.check_requirements"
                placeholder="自动带出"
                size="small"
                readonly
              />
            </td>
            <td>
              <input
                :id="`brief_description_${index}`"
                :name="`brief_description_${index}`"
                v-model="item.brief_description"
                type="text"
                class="table-input"
                placeholder="请输入"
              >
            </td>
            <td class="action-cell">
              <a
                href="#"
                class="action-link action-delete"
                @click.prevent="$emit('remove', index)"
              >删除</a>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="table-actions">
        <button
          class="btn btn-add-small"
          @click="$emit('add')"
        >
          添加
        </button>
        <button
          v-if="showImport"
          class="btn btn-import"
          @click="$emit('import')"
        >
          导入事项
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElSelect, ElOption, ElInput } from 'element-plus'

export interface InspectionItem {
  item_id?: string
  inspection_item?: string
  inspection_content?: string
  check_requirements?: string
  brief_description?: string
  level1_id?: string
  level1_name?: string
  level2_id?: string
  level2_name?: string
  level3_id?: string
  level3_name?: string
}

export interface InspectionTreeNode {
  id: string
  label: string
  level: number
  checkRequirement?: string
  checkStandard?: string
  children?: InspectionTreeNode[]
}

const props = withDefaults(defineProps<{
  title?: string
  items: InspectionItem[]
  treeData: InspectionTreeNode[]
  showImport?: boolean
}>(), {
  title: '维保事项',
  showImport: false,
})

defineEmits<{
  'update:items': [items: InspectionItem[]]
  'add': []
  'remove': [index: number]
  'import': []
}>()

const level1Nodes = computed(() => {
  return props.treeData.filter((node) => node.level === 1)
})

const getLevel2Nodes = (level1Id: string | undefined): InspectionTreeNode[] => {
  if (!level1Id) return []
  const level1Node = props.treeData.find((node) => node.id === level1Id)
  return level1Node?.children || []
}

const getLevel3Nodes = (level1Id: string | undefined, level2Id: string | undefined): InspectionTreeNode[] => {
  if (!level1Id || !level2Id) return []
  const level2Nodes = getLevel2Nodes(level1Id)
  const level2Node = level2Nodes.find((node) => node.id === level2Id)
  return level2Node?.children || []
}

const handleLevelChange = (level: number, index: number) => {
  const item = props.items[index]
  
  if (level === 1) {
    item.level2_id = ''
    item.level2_name = ''
    item.level3_id = ''
    item.level3_name = ''
    item.check_requirements = ''
    item.inspection_item = ''
    item.inspection_content = ''
    
    if (item.level1_id) {
      const level1Node = level1Nodes.value.find((node) => node.id === item.level1_id)
      if (level1Node) {
        item.level1_name = level1Node.label
      }
    }
  } else if (level === 2) {
    item.level3_id = ''
    item.level3_name = ''
    item.check_requirements = ''
    item.inspection_content = ''
    
    if (item.level1_id && item.level2_id) {
      const level2Nodes = getLevel2Nodes(item.level1_id)
      const level2Node = level2Nodes.find((node) => node.id === item.level2_id)
      if (level2Node) {
        item.inspection_item = level2Node.label
        item.level2_name = level2Node.label
      }
    }
  } else if (level === 3) {
    item.check_requirements = ''
    
    if (item.level1_id && item.level2_id && item.level3_id) {
      const level3Nodes = getLevel3Nodes(item.level1_id, item.level2_id)
      const level3Node = level3Nodes.find((node) => node.id === item.level3_id)
      if (level3Node) {
        item.inspection_content = level3Node.label
        item.check_requirements = level3Node.checkRequirement || ''
        item.level3_name = level3Node.label
      }
    }
  }
}

const clearLevel = (level: number, item: InspectionItem) => {
  if (level === 1) {
    item.level1_id = ''
    item.level1_name = ''
    item.level2_id = ''
    item.level2_name = ''
    item.level3_id = ''
    item.level3_name = ''
    item.check_requirements = ''
    item.inspection_item = ''
    item.inspection_content = ''
  } else if (level === 2) {
    item.level2_id = ''
    item.level2_name = ''
    item.level3_id = ''
    item.level3_name = ''
    item.check_requirements = ''
    item.inspection_item = ''
    item.inspection_content = ''
  } else if (level === 3) {
    item.level3_id = ''
    item.level3_name = ''
    item.check_requirements = ''
    item.inspection_content = ''
  }
}
</script>

<style scoped>
.inspection-items-table {
  margin-top: 20px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
  padding-left: 10px;
  border-left: 3px solid #409eff;
}

.table-section-inner {
  background: var(--color-bg-page);
  border-radius: 6px;
  padding: 12px;
}

.inner-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--color-bg-card);
  border-radius: 4px;
  overflow: hidden;
}

.inner-table th,
.inner-table td {
  padding: 10px 12px;
  text-align: left;
  border: 1px solid #ebeef5;
  font-size: 13px;
}

.inner-table th {
  background: var(--color-bg-page);
  font-weight: 600;
  color: #303133;
}

.table-input {
  width: 100%;
  padding: 6px 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 13px;
}

.table-input-readonly {
  background: var(--color-bg-page);
  cursor: not-allowed;
}

.selected-text {
  padding: 6px 10px;
  background: #ecf5ff;
  border-radius: 4px;
  color: #409eff;
  cursor: pointer;
  font-size: 13px;
}

.selected-text:hover {
  background: #d9ecff;
}

.action-cell {
  text-align: center;
}

.action-link {
  text-decoration: none;
  font-size: 13px;
  color: #f56c6c;
  cursor: pointer;
}

.action-link:hover {
  text-decoration: underline;
}

.table-actions {
  display: flex;
  gap: 10px;
  margin-top: 12px;
}

.btn {
  padding: 6px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.btn-add-small {
  background: #409eff;
  color: white;
}

.btn-add-small:hover {
  background: #66b1ff;
}

.btn-import {
  background: #67c23a;
  color: white;
}

.btn-import:hover {
  background: #85ce61;
}
</style>
