<template>
  <div class="bar-chart horizontal-bar-chart">
    <div v-for="(item, index) in data" :key="index" class="bar-item">
      <div class="bar-label">{{ item.name }}</div>
      <div class="bar-wrapper">
        <div class="bar" :style="{ width: getBarWidth(item.value) + '%' }"></div>
        <div class="bar-value">{{ item.value }}</div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue'
import type { WorkByPerson } from '@/types/api'

interface Props {
  data: WorkByPerson[]
  maxValue: number
}

const props = defineProps<Props>()

const getBarWidth = (value: number): number => {
  if (props.maxValue === 0) return 0
  return (value / props.maxValue) * 100
}
</script>

<style scoped>
.bar-chart {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  flex: 1;
}

.horizontal-bar-chart {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  flex: 1;
}

.bar-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.bar-label {
  min-width: 100px;
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  font-weight: 500;
}

.bar-wrapper {
  flex: 1;
  height: 40px;
  background: var(--color-border-light);
  border-radius: var(--radius-sm);
  overflow: hidden;
  display: flex;
  align-items: center;
}

.bar {
  height: 100%;
  background: linear-gradient(90deg, var(--color-success) 0%, var(--color-success-light) 100%);
  transition: width var(--transition-slow) ease;
}

.bar-value {
  margin-left: var(--spacing-lg);
  font-weight: 600;
  font-size: var(--font-size-lg);
  color: var(--color-text-primary);
  min-width: 60px;
}
</style>
