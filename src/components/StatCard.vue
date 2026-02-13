<template>
  <div
    class="stat-card"
    :class="[cardClass, { 'edit-mode': isEditMode }]"
    :draggable="isEditMode"
    @dragstart="$emit('dragstart', $event)"
    @dragover="$emit('dragover', $event)"
    @drop="$emit('drop', $event)"
  >
    <div class="card-actions" v-if="isEditMode">
      <button class="action-btn" @click="$emit('toggle-visibility')">
        {{ visible ? '隐藏' : '显示' }}
      </button>
    </div>
    <div class="card-label">{{ label }}</div>
    <div class="card-value">{{ value }}</div>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue'

interface Props {
  id: string
  label: string
  value: number
  visible: boolean
  isEditMode: boolean
}

const props = defineProps<Props>()

defineEmits<{
  dragstart: [event: DragEvent]
  dragover: [event: DragEvent]
  drop: [event: DragEvent]
  'toggle-visibility': []
}>()

const cardClass = computed(() => {
  const classMap: Record<string, string> = {
    'near-expiry': 'card-near-expiry',
    'overdue': 'card-overdue',
    'completed': 'card-completed',
    'regular': 'card-regular',
    'temporary': 'card-temporary',
    'sporadic': 'card-sporadic'
  }
  return classMap[props.id] || ''
})
</script>

<style scoped>
.stat-card {
  background: white;
  border-radius: var(--radius-xl);
  padding: var(--spacing-3xl) var(--spacing-xl);
  box-shadow: var(--shadow-sm);
  transition: transform var(--transition-normal), box-shadow var(--transition-normal);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md);
  min-height: 160px;
  text-align: center;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.stat-card.edit-mode {
  cursor: move;
  border: 2px dashed var(--color-success);
}

.stat-card.edit-mode:hover {
  border-color: var(--color-success-dark);
}

.card-actions {
  position: absolute;
  top: var(--spacing-md);
  right: var(--spacing-md);
  display: flex;
  gap: var(--spacing-xs);
}

.action-btn {
  padding: var(--spacing-xs) var(--spacing-md);
  font-size: var(--font-size-xs);
  background: var(--color-success);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background var(--transition-normal);
}

.action-btn:hover {
  background: var(--color-success-dark);
}

.card-label {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  font-weight: 500;
}

.card-value {
  font-size: 56px;
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1;
}

.card-near-expiry {
  border-left: 4px solid var(--color-danger);
}

.card-overdue {
  border-left: 4px solid var(--color-danger-dark);
}

.card-completed {
  border-left: 4px solid var(--color-success);
}

.card-regular {
  border-left: 4px solid var(--color-info);
}

.card-temporary {
  border-left: 4px solid var(--color-warning);
}

.card-sporadic {
  border-left: 4px solid var(--color-purple);
}
</style>
