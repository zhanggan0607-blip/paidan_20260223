<template>
  <div class="skeleton" :class="{ 'skeleton--animated': animated }">
    <div 
      v-if="type === 'text'" 
      class="skeleton-text"
      :style="{ width: width, height: height || '16px' }"
    />
    <div 
      v-else-if="type === 'avatar'" 
      class="skeleton-avatar"
      :style="{ width: size || '48px', height: size || '48px' }"
    />
    <div 
      v-else-if="type === 'image'" 
      class="skeleton-image"
      :style="{ width: width || '100%', height: height || '200px' }"
    />
    <div 
      v-else-if="type === 'button'" 
      class="skeleton-button"
      :style="{ width: width || '80px', height: height || '36px' }"
    />
    <div v-else-if="type === 'card'" class="skeleton-card">
      <div class="skeleton-card__header">
        <div class="skeleton-avatar" style="width: 40px; height: 40px;"></div>
        <div class="skeleton-card__title">
          <div class="skeleton-text" style="width: 60%; height: 14px;"></div>
          <div class="skeleton-text" style="width: 40%; height: 12px; margin-top: 8px;"></div>
        </div>
      </div>
      <div class="skeleton-card__content">
        <div class="skeleton-text" style="width: 100%; height: 12px;"></div>
        <div class="skeleton-text" style="width: 90%; height: 12px; margin-top: 8px;"></div>
        <div class="skeleton-text" style="width: 75%; height: 12px; margin-top: 8px;"></div>
      </div>
    </div>
    <div v-else-if="type === 'list'" class="skeleton-list">
      <div v-for="i in rows" :key="i" class="skeleton-list__item">
        <div class="skeleton-avatar" style="width: 32px; height: 32px;"></div>
        <div class="skeleton-list__content">
          <div class="skeleton-text" style="width: 70%; height: 14px;"></div>
          <div class="skeleton-text" style="width: 50%; height: 12px; margin-top: 6px;"></div>
        </div>
      </div>
    </div>
    <div v-else-if="type === 'table'" class="skeleton-table">
      <div class="skeleton-table__header">
        <div v-for="i in columns" :key="i" class="skeleton-text" style="height: 14px;"></div>
      </div>
      <div v-for="i in rows" :key="i" class="skeleton-table__row">
        <div v-for="j in columns" :key="j" class="skeleton-text" style="height: 14px;"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  type: {
    type: String,
    default: 'text',
    validator: (value: string) => ['text', 'avatar', 'image', 'button', 'card', 'list', 'table'].includes(value)
  },
  width: {
    type: String,
    default: ''
  },
  height: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: ''
  },
  rows: {
    type: Number,
    default: 3
  },
  columns: {
    type: Number,
    default: 4
  },
  animated: {
    type: Boolean,
    default: true
  }
})
</script>

<style scoped>
.skeleton {
  display: inline-block;
}

.skeleton--animated .skeleton-text,
.skeleton--animated .skeleton-avatar,
.skeleton--animated .skeleton-image,
.skeleton--animated .skeleton-button {
  background: var(--skeleton-color);
  background-image: var(--skeleton-highlight);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s ease-in-out infinite;
}

.skeleton-text {
  border-radius: var(--border-radius-sm);
  background: var(--skeleton-color);
}

.skeleton-avatar {
  border-radius: 50%;
  background: var(--skeleton-color);
}

.skeleton-image {
  border-radius: var(--border-radius-md);
  background: var(--skeleton-color);
}

.skeleton-button {
  border-radius: var(--border-radius-sm);
  background: var(--skeleton-color);
}

.skeleton-card {
  background: var(--color-bg-card);
  border-radius: var(--border-radius-md);
  padding: var(--card-padding);
  border: 1px solid var(--color-border-light);
}

.skeleton-card__header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.skeleton-card__title {
  flex: 1;
}

.skeleton-card__content {
  margin-top: var(--spacing-md);
}

.skeleton-list__item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--color-border-lighter);
}

.skeleton-list__item:last-child {
  border-bottom: none;
}

.skeleton-list__content {
  flex: 1;
}

.skeleton-table__header {
  display: grid;
  gap: var(--spacing-md);
  padding: var(--spacing-sm) 0;
  border-bottom: 2px solid var(--color-border);
  margin-bottom: var(--spacing-sm);
}

.skeleton-table__row {
  display: grid;
  gap: var(--spacing-md);
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--color-border-lighter);
}

@keyframes skeleton-loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>