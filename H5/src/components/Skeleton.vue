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
      :style="{ width: width || '80px', height: height || '44px' }"
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
      <van-skeleton v-for="i in rows" :key="i" title avatar :row="2" />
    </div>
    <div v-else-if="type === 'work-order'" class="skeleton-work-order">
      <div class="skeleton-work-order__header">
        <div class="skeleton-text" style="width: 70%; height: 18px;"></div>
        <div class="skeleton-text" style="width: 60px; height: 24px; border-radius: 12px;"></div>
      </div>
      <div class="skeleton-work-order__info">
        <div class="skeleton-text" style="width: 50%; height: 14px;"></div>
        <div class="skeleton-text" style="width: 40%; height: 14px;"></div>
      </div>
      <div class="skeleton-work-order__content">
        <div class="skeleton-text" style="width: 100%; height: 12px;"></div>
        <div class="skeleton-text" style="width: 90%; height: 12px; margin-top: 6px;"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  type: {
    type: String,
    default: 'text',
    validator: (value: string) => ['text', 'avatar', 'image', 'button', 'card', 'list', 'work-order'].includes(value)
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
  animated: {
    type: Boolean,
    default: true
  }
})
</script>

<style scoped>
.skeleton {
  display: inline-block;
  width: 100%;
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
  margin: var(--spacing-sm);
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

.skeleton-list {
  padding: var(--spacing-sm);
}

.skeleton-list :deep(.van-skeleton) {
  padding: var(--spacing-md) 0;
  border-bottom: 1px solid var(--color-border-lighter);
}

.skeleton-work-order {
  background: var(--color-bg-card);
  border-radius: var(--border-radius-md);
  padding: var(--card-padding);
  margin: var(--spacing-sm);
}

.skeleton-work-order__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-sm);
}

.skeleton-work-order__info {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--spacing-sm);
}

.skeleton-work-order__content {
  padding-top: var(--spacing-sm);
  border-top: 1px solid var(--color-border-lighter);
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