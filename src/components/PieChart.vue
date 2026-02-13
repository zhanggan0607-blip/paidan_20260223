<template>
  <div class="pie-chart">
    <div class="pie-chart-container">
      <svg viewBox="0 0 100 100" class="pie-svg">
        <circle
          cx="50"
          cy="50"
          r="40"
          fill="none"
          stroke-width="20"
          :stroke-dasharray="`${onTimeDash} ${251.2 - onTimeDash}`"
          :stroke="onTimeColor"
          transform="rotate(-90 50 50)"
        />
        <circle
          cx="50"
          cy="50"
          r="40"
          fill="none"
          stroke-width="20"
          :stroke-dasharray="`${delayedDash} ${251.2 - delayedDash}`"
          :stroke="delayedColor"
          transform="rotate(-90 50 50)"
        />
      </svg>
    </div>
    <div class="pie-legend">
      <div class="legend-item">
        <div class="legend-color legend-color-delayed"></div>
        <span>延期完成（{{ delayedPercent }}%）</span>
      </div>
      <div class="legend-item">
        <div class="legend-color legend-color-ontime"></div>
        <span>预期完成（{{ onTimePercent }}%）</span>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue'

interface Props {
  onTimeRate: number
  onTimeColor?: string
  delayedColor?: string
}

const props = withDefaults(defineProps<Props>(), {
  onTimeColor: '#4CAF50',
  delayedColor: '#FF6B6B'
})

const onTimePercent = computed(() => Math.round(props.onTimeRate * 100))
const delayedPercent = computed(() => Math.round((1 - props.onTimeRate) * 100))
const onTimeDash = computed(() => props.onTimeRate * 251.2)
const delayedDash = computed(() => (1 - props.onTimeRate) * 251.2)
</script>

<style scoped>
.pie-chart {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 48px;
  flex: 1;
}

.pie-chart-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.pie-svg {
  width: 240px;
  height: 240px;
}

.pie-legend {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: var(--radius-sm);
}

.legend-color-delayed {
  background: var(--color-danger);
}

.legend-color-ontime {
  background: var(--color-success);
}
</style>
