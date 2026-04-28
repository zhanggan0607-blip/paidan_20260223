<template>
  <div class="virtual-scroll-container">
    <div
      ref="containerRef"
      class="scroll-content"
      :style="{ height: `${height}px`, overflowY: 'auto' }"
      @scroll="handleScroll"
    >
      <div
        :style="{ height: `${totalHeight}px`, position: 'relative' }"
      >
        <div
          :style="{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            transform: `translateY(${offset}px)`,
          }"
        >
          <div
            v-for="(item, idx) in visibleItems"
            :key="getItemKey(item, startIndex + idx)"
            class="virtual-item"
            :style="{ height: `${itemHeight}px` }"
          >
            <slot
              name="item"
              :item="item"
              :index="startIndex + idx"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  items: unknown[]
  itemHeight: number
  height: number
  buffer?: number
  getItemKey: (item: unknown, index: number) => string | number
}

const props = withDefaults(defineProps<Props>(), {
  buffer: 5,
})

const emit = defineEmits<{
  'scroll': [scrollTop: number]
}>()

const scrollTop = ref(0)

const visibleCount = computed(() => {
  return Math.ceil(props.height / props.itemHeight) + props.buffer * 2
})

const totalHeight = computed(() => {
  return props.items.length * props.itemHeight
})

const startIndex = computed(() => {
  return Math.max(0, Math.floor(scrollTop.value / props.itemHeight) - props.buffer)
})

const endIndex = computed(() => {
  return Math.min(
    props.items.length - 1,
    startIndex.value + visibleCount.value
  )
})

const visibleItems = computed(() => {
  return props.items.slice(startIndex.value, endIndex.value + 1)
})

const offset = computed(() => {
  return startIndex.value * props.itemHeight
})

const handleScroll = (event: Event) => {
  const target = event.target as HTMLElement
  scrollTop.value = target.scrollTop
  emit('scroll', scrollTop.value)
}
</script>

<style scoped>
.virtual-scroll-container {
  width: 100%;
}

.scroll-content {
  width: 100%;
  position: relative;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.virtual-item {
  width: 100%;
  box-sizing: border-box;
}
</style>
