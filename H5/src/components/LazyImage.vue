<template>
  <div class="lazy-image-container" ref="containerRef">
    <div v-if="loading" class="image-placeholder">
      <van-loading size="20" />
    </div>
    <img
      v-show="!loading && loaded"
      ref="imgRef"
      :src="imageSrc"
      :alt="alt"
      class="lazy-image"
      :style="imgStyle"
      @load="onLoad"
      @error="onError"
    />
    <div v-if="error" class="image-error">
      <van-icon name="photo-fail" size="24" />
      <span>加载失败</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps<{
  src: string
  alt?: string
  thumbnailSize?: number
  width?: string | number
  height?: string | number
  lazy?: boolean
}>()

const containerRef = ref<HTMLElement | null>(null)
const imgRef = ref<HTMLImageElement | null>(null)
const loading = ref(true)
const loaded = ref(false)
const error = ref(false)
const isVisible = ref(false)

const imageSrc = computed(() => {
  if (!props.src) return ''
  
  if (props.thumbnailSize && props.src.includes('/uploads/')) {
    const match = props.src.match(/\/uploads\/(\d{8})\/(.+)$/)
    if (match) {
      const [, date, filename] = match
      return `/api/v1/files/thumbnail/${date}/${filename}?size=${props.thumbnailSize}`
    }
  }
  
  return props.src
})

const imgStyle = computed(() => ({
  width: typeof props.width === 'number' ? `${props.width}px` : props.width,
  height: typeof props.height === 'number' ? `${props.height}px` : props.height,
}))

let observer: IntersectionObserver | null = null

const onLoad = () => {
  loading.value = false
  loaded.value = true
  error.value = false
}

const onError = () => {
  loading.value = false
  loaded.value = false
  error.value = true
}

const startLoading = () => {
  if (imgRef.value && imageSrc.value) {
    imgRef.value.src = imageSrc.value
  }
}

onMounted(() => {
  if (!props.lazy) {
    isVisible.value = true
    return
  }
  
  if (containerRef.value && 'IntersectionObserver' in window) {
    observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            isVisible.value = true
            startLoading()
            observer?.disconnect()
          }
        })
      },
      {
        rootMargin: '50px',
        threshold: 0.1,
      }
    )
    
    observer.observe(containerRef.value)
  } else {
    isVisible.value = true
    startLoading()
  }
})

onUnmounted(() => {
  observer?.disconnect()
})

watch(isVisible, (val) => {
  if (val && !loaded.value && !error.value) {
    startLoading()
  }
})
</script>

<style scoped>
.lazy-image-container {
  position: relative;
  display: inline-block;
  overflow: hidden;
  background-color: #f7f8fa;
}

.lazy-image {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f7f8fa;
}

.image-error {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  background-color: #f7f8fa;
  color: #969799;
  font-size: 12px;
}
</style>
