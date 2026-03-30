<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  showSuccessToast,
  showFailToast,
  showConfirmDialog,
  showLoadingToast,
  closeToast,
} from 'vant'
import { periodicInspectionService } from '../services'
import { useNavigation } from '../composables'

const router = useRouter()
const route = useRoute()
const { goBack } = useNavigation()

const canvas = ref<HTMLCanvasElement | null>(null)
const ctx = ref<CanvasRenderingContext2D | null>(null)
const isDrawing = ref(false)
const lastX = ref(0)
const lastY = ref(0)
const signatureData = ref('')
const isIOS = ref(false)

const isIPhone = () => {
  return /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)
}

const handleOrientationChange = () => {
  setTimeout(() => {
    initCanvas()
  }, 300)
}

const initCanvas = async () => {
  if (!canvas.value) return

  const container = canvas.value.parentElement
  if (!container) return

  await nextTick()

  const rect = container.getBoundingClientRect()
  const dpr = window.devicePixelRatio || 1

  canvas.value.width = rect.width * dpr
  canvas.value.height = rect.height * dpr
  canvas.value.style.width = rect.width + 'px'
  canvas.value.style.height = rect.height + 'px'

  ctx.value = canvas.value.getContext('2d', { willReadFrequently: true })
  if (ctx.value) {
    ctx.value.scale(dpr, dpr)
    ctx.value.strokeStyle = '#000'
    ctx.value.lineWidth = 3
    ctx.value.lineCap = 'round'
    ctx.value.lineJoin = 'round'
    ctx.value.fillStyle = '#fff'
    ctx.value.fillRect(0, 0, rect.width, rect.height)
  }
}

const getCoordinates = (e: TouchEvent | MouseEvent) => {
  if (!canvas.value) return { x: 0, y: 0 }

  const rect = canvas.value.getBoundingClientRect()

  if (e.type.startsWith('touch')) {
    const touch = (e as TouchEvent).touches[0] ?? (e as TouchEvent).changedTouches[0]
    if (!touch) return { x: 0, y: 0 }
    return {
      x: (touch.clientX - rect.left),
      y: (touch.clientY - rect.top),
    }
  } else {
    return {
      x: (e as MouseEvent).clientX - rect.left,
      y: (e as MouseEvent).clientY - rect.top,
    }
  }
}

const startDrawing = (e: TouchEvent | MouseEvent) => {
  if (e.cancelable) {
    e.preventDefault()
  }
  isDrawing.value = true
  const coords = getCoordinates(e)
  lastX.value = coords.x
  lastY.value = coords.y
}

const draw = (e: TouchEvent | MouseEvent) => {
  if (e.cancelable) {
    e.preventDefault()
  }
  if (!isDrawing.value || !ctx.value) return

  const coords = getCoordinates(e)

  ctx.value.beginPath()
  ctx.value.moveTo(lastX.value, lastY.value)
  ctx.value.lineTo(coords.x, coords.y)
  ctx.value.stroke()

  lastX.value = coords.x
  lastY.value = coords.y
}

const stopDrawing = () => {
  isDrawing.value = false
}

const handleClear = async () => {
  try {
    await showConfirmDialog({
      title: '提示',
      message: '确认清除签名吗？',
    })

    if (ctx.value && canvas.value) {
      ctx.value.fillStyle = '#fff'
      ctx.value.fillRect(0, 0, canvas.value.width, canvas.value.height)
    }
  } catch {}
}

const handleConfirm = async () => {
  if (!canvas.value) return

  const isEmpty = isCanvasEmpty()
  if (isEmpty) {
    showFailToast('请先签名')
    return
  }

  signatureData.value = canvas.value.toDataURL('image/png')

  const from = route.query.from as string
  const type = route.query.type as string
  const inspectionId = route.query.inspectionId as string
  const signatureType = route.query.signatureType as string

  if (type === 'periodic-inspection' && inspectionId) {
    showLoadingToast({ message: '保存签名...', forbidClick: true })
    try {
      const response = await periodicInspectionService.patch(Number(inspectionId), {
        signature: signatureData.value,
      } as any)
      if (response.code === 200) {
        localStorage.setItem('periodic_inspection_signature', signatureData.value)
        showSuccessToast('签名保存成功')
        router.replace(from || '/periodic-inspection')
      } else {
        showFailToast('签名保存失败')
      }
    } catch (error) {
      console.error('Failed to save signature:', error)
      showFailToast('签名保存失败')
    } finally {
      closeToast()
    }
  } else if (from) {
    if (type === 'periodic-inspection') {
      localStorage.setItem('periodic_inspection_signature', signatureData.value)
    } else if (type === 'temporary-repair') {
      // 根据签字类型保存到不同的 localStorage key
      if (signatureType === 'customer') {
        localStorage.setItem('temporary_repair_customer_signature', signatureData.value)
      } else {
        localStorage.setItem('temporary_repair_signature', signatureData.value)
      }
    } else if (type === 'temporary-repair-create') {
      localStorage.setItem('temporary_repair_create_signature', signatureData.value)
    } else if (type === 'spot-work') {
      localStorage.setItem('spot_work_signature', signatureData.value)
    } else if (type === 'spot-work-apply') {
      localStorage.setItem('spot_work_apply_signature', signatureData.value)
    }

    showSuccessToast('签名成功')
    router.replace(from)
  } else {
    goBack()
  }
}

const handleBack = () => {
  goBack()
}

const isCanvasEmpty = () => {
  if (!canvas.value || !ctx.value) return true

  const pixelData = ctx.value.getImageData(0, 0, canvas.value.width, canvas.value.height).data
  for (let i = 0; i < pixelData.length; i += 4) {
    const r = pixelData[i]
    const g = pixelData[i + 1]
    const b = pixelData[i + 2]
    if (r !== 255 || g !== 255 || b !== 255) {
      return false
    }
  }
  return true
}

onMounted(() => {
  isIOS.value = isIPhone()
  handleOrientationChange()
  setTimeout(() => {
    initCanvas()
  }, isIOS.value ? 500 : 300)
  window.addEventListener('resize', initCanvas)
  window.addEventListener('orientationchange', handleOrientationChange)
})

onUnmounted(() => {
  window.removeEventListener('resize', initCanvas)
  window.removeEventListener('orientationchange', handleOrientationChange)
})
</script>

<template>
  <div class="signature-page">
    <div class="signature-header">
      <van-icon name="arrow-left" size="24" @click="handleBack" />
      <span class="title">签字确认</span>
      <div class="placeholder"></div>
    </div>

    <div class="signature-container">
      <div class="canvas-wrapper">
        <canvas
          ref="canvas"
          class="signature-canvas"
          @mousedown="startDrawing"
          @mousemove="draw"
          @mouseup="stopDrawing"
          @mouseleave="stopDrawing"
          @touchstart="startDrawing"
          @touchmove="draw"
          @touchend="stopDrawing"
        />
      </div>

      <div class="signature-tip">请在上方区域签名</div>
    </div>

    <div class="action-buttons">
      <van-button type="default" size="small" @click="handleClear">清除</van-button>
      <van-button type="primary" size="small" @click="handleConfirm">确认</van-button>
    </div>
  </div>
</template>

<style scoped>
.signature-page {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  height: 100dvh;
  background-color: #f5f7fa;
  display: flex;
  flex-direction: column;
  padding-top: env(safe-area-inset-top);
  padding-bottom: env(safe-area-inset-bottom);
}

.signature-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  padding-top: calc(8px + env(safe-area-inset-top));
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.title {
  font-size: 16px;
  font-weight: 500;
}

.placeholder {
  width: 24px;
}

.signature-container {
  flex: 1;
  padding: 12px;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.canvas-wrapper {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  border: 2px dashed #dcdee0;
  overflow: hidden;
  min-height: 0;
}

.signature-canvas {
  width: 100%;
  height: 100%;
  touch-action: none;
  display: block;
}

.signature-tip {
  text-align: center;
  padding: 8px;
  color: #969799;
  font-size: 13px;
  flex-shrink: 0;
}

.action-buttons {
  padding: 10px 24px;
  background: #fff;
  display: flex;
  justify-content: center;
  gap: 32px;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.action-buttons .van-button {
  min-width: 100px;
}

@media screen and (orientation: landscape) {
  .signature-header {
    padding: 6px 20px;
  }

  .title {
    font-size: 14px;
  }

  .signature-container {
    padding: 8px 16px;
  }

  .signature-tip {
    padding: 4px;
    font-size: 12px;
  }

  .action-buttons {
    padding: 6px 24px;
  }

  .action-buttons .van-button {
    min-width: 80px;
    font-size: 13px;
  }
}
</style>
