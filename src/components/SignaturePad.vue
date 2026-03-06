<template>
  <div class="signature-pad">
    <div class="signature-canvas-wrapper">
      <canvas
        ref="canvasRef"
        class="signature-canvas"
        @mousedown="startDrawing"
        @mousemove="draw"
        @mouseup="stopDrawing"
        @mouseleave="stopDrawing"
        @touchstart="handleTouchStart"
        @touchmove="handleTouchMove"
        @touchend="stopDrawing"
      ></canvas>
      <div v-if="!hasDrawn" class="signature-placeholder">请在此处签名</div>
    </div>
    <div class="signature-actions">
      <button class="btn btn-clear" @click="clearSignature">清除</button>
      <button class="btn btn-confirm" :disabled="!hasDrawn" @click="confirmSignature">确认</button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onUnmounted, nextTick } from 'vue'

export default defineComponent({
  name: 'SignaturePad',
  emits: ['confirm', 'cancel'],
  setup(_props, { emit }) {
    const canvasRef = ref<HTMLCanvasElement | null>(null)
    const isDrawing = ref(false)
    const hasDrawn = ref(false)
    let ctx: CanvasRenderingContext2D | null = null
    let lastX = 0
    let lastY = 0

    const initCanvas = () => {
      const canvas = canvasRef.value
      if (!canvas) return

      const wrapper = canvas.parentElement
      if (!wrapper) return

      canvas.width = wrapper.clientWidth
      canvas.height = 200

      ctx = canvas.getContext('2d')
      if (ctx) {
        ctx.strokeStyle = '#000'
        ctx.lineWidth = 2
        ctx.lineCap = 'round'
        ctx.lineJoin = 'round'
        ctx.fillStyle = '#fff'
        ctx.fillRect(0, 0, canvas.width, canvas.height)
      }
    }

    const getCoordinates = (event: MouseEvent | TouchEvent) => {
      const canvas = canvasRef.value
      if (!canvas) return { x: 0, y: 0 }

      const rect = canvas.getBoundingClientRect()
      let clientX: number, clientY: number

      if (event instanceof TouchEvent) {
        clientX = event.touches[0].clientX
        clientY = event.touches[0].clientY
      } else {
        clientX = event.clientX
        clientY = event.clientY
      }

      return {
        x: clientX - rect.left,
        y: clientY - rect.top,
      }
    }

    const startDrawing = (event: MouseEvent | TouchEvent) => {
      isDrawing.value = true
      hasDrawn.value = true
      const coords = getCoordinates(event)
      lastX = coords.x
      lastY = coords.y
    }

    const draw = (event: MouseEvent | TouchEvent) => {
      if (!isDrawing.value || !ctx) return

      const coords = getCoordinates(event)
      ctx.beginPath()
      ctx.moveTo(lastX, lastY)
      ctx.lineTo(coords.x, coords.y)
      ctx.stroke()

      lastX = coords.x
      lastY = coords.y
    }

    const stopDrawing = () => {
      isDrawing.value = false
    }

    const handleTouchStart = (event: TouchEvent) => {
      event.preventDefault()
      startDrawing(event)
    }

    const handleTouchMove = (event: TouchEvent) => {
      event.preventDefault()
      draw(event)
    }

    const clearSignature = () => {
      const canvas = canvasRef.value
      if (!canvas || !ctx) return

      ctx.fillStyle = '#fff'
      ctx.fillRect(0, 0, canvas.width, canvas.height)
      hasDrawn.value = false
    }

    const confirmSignature = () => {
      const canvas = canvasRef.value
      if (!canvas || !hasDrawn.value) return

      const dataUrl = canvas.toDataURL('image/png')
      emit('confirm', dataUrl)
    }

    const handleResize = () => {
      const canvas = canvasRef.value
      if (!canvas) return

      const tempCanvas = document.createElement('canvas')
      tempCanvas.width = canvas.width
      tempCanvas.height = canvas.height
      const tempCtx = tempCanvas.getContext('2d')
      if (tempCtx) {
        tempCtx.drawImage(canvas, 0, 0)
      }

      initCanvas()

      if (ctx && tempCtx) {
        ctx.drawImage(tempCanvas, 0, 0)
      }
    }

    onMounted(() => {
      nextTick(() => {
        initCanvas()
        window.addEventListener('resize', handleResize)
      })
    })

    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
    })

    return {
      canvasRef,
      isDrawing,
      hasDrawn,
      startDrawing,
      draw,
      stopDrawing,
      handleTouchStart,
      handleTouchMove,
      clearSignature,
      confirmSignature,
    }
  },
})
</script>

<style scoped>
.signature-pad {
  width: 100%;
}

.signature-canvas-wrapper {
  position: relative;
  width: 100%;
  border: 1px solid #d0d7de;
  border-radius: 4px;
  background: #fff;
  overflow: hidden;
}

.signature-canvas {
  display: block;
  width: 100%;
  cursor: crosshair;
  touch-action: none;
}

.signature-placeholder {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #999;
  font-size: 16px;
  pointer-events: none;
}

.signature-actions {
  display: flex;
  gap: 12px;
  margin-top: 12px;
  justify-content: flex-end;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-clear {
  background: #fff;
  color: #666;
  border: 1px solid #d0d7de;
}

.btn-clear:hover {
  background: #f5f5f5;
}

.btn-confirm {
  background: #1976d2;
  color: #fff;
}

.btn-confirm:hover:not(:disabled) {
  background: #1565c0;
}

.btn-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
