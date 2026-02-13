<template>
  <div class="bar-chart vertical-bar-chart">
    <div class="vertical-bars">
      <div v-for="(item, index) in data" :key="index" class="vertical-bar-item">
        <div class="vertical-bar-wrapper">
          <div class="vertical-bar" :style="{ height: getBarHeight(item.value) + '%' }"></div>
          <div class="vertical-bar-value">{{ item.value }}</div>
        </div>
        <div class="vertical-bar-label">{{ item.name }}</div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue'
import type { TopProject } from '@/types/api'

interface Props {
  data: TopProject[]
  maxValue: number
}

const props = defineProps<Props>()

const getBarHeight = (value: number): number => {
  if (props.maxValue === 0) return 0
  return (value / props.maxValue) * 100
}
</script>

<style scoped>
.bar-chart {
  display: flex;
  align-items: flex-end;
  height: 350px;
  gap: var(--spacing-xl);
  flex: 1;
}

.vertical-bars {
  display: flex;
  align-items: flex-end;
  height: 100%;
  gap: var(--spacing-xl);
  flex: 1;
}

.vertical-bar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm);
}

.vertical-bar-wrapper {
  width: 100%;
  max-width: 100px;
  height: 100%;
  background: var(--color-border-light);
  border-radius: var(--radius-sm);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: center;
}

.vertical-bar {
  width: 100%;
  background: linear-gradient(180deg, var(--color-success) 0%, var(--color-success-dark) 100%);
  transition: height var(--transition-slow) ease;
}

.vertical-bar-value {
  margin-bottom: var(--spacing-md);
  font-weight: 600;
  font-size: var(--font-size-lg);
  color: var(--color-text-primary);
}

.vertical-bar-label {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  font-weight: 500;
  text-align: center;
}
</style>
