<template>
  <div class="photo-upload">
    <div class="photo-grid">
      <div
        v-for="(photo, index) in photos"
        :key="index"
        class="photo-item"
      >
        <img
          :src="photo"
          alt="现场图片"
          loading="lazy"
          @click="previewPhoto(photo)"
        >
        <button
          class="delete-btn"
          title="删除"
          @click.stop="removePhoto(index)"
        >
          ×
        </button>
      </div>
      <div
        v-if="photos.length < maxCount"
        class="photo-add"
      >
        <input
          id="photoUpload"
          ref="fileInputRef"
          type="file"
          name="photo"
          accept="image/*"
          multiple
          style="display: none"
          @change="handleFileSelect"
        >
        <button
          class="add-btn"
          :disabled="uploading"
          @click="triggerFileSelect"
        >
          <span class="add-icon">+</span>
          <span class="add-text">{{ uploading ? '上传中...' : '添加图片' }}</span>
        </button>
      </div>
    </div>
    <div class="photo-tip">
      支持 jpg、png 格式，单张不超过 5MB，最多 {{ maxCount }} 张，可多选
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { request } from '@/api/request'

export default defineComponent({
  name: 'PhotoUpload',
  props: {
    modelValue: {
      type: Array as () => string[],
      default: (): any[] => [],
    },
    maxCount: {
      type: Number,
      default: 9,
    },
    maxSize: {
      type: Number,
      default: 5 * 1024 * 1024,
    },
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const photos = ref<string[]>([...props.modelValue])
    const fileInputRef = ref<HTMLInputElement | null>(null)
    const uploading = ref(false)

    watch(
      () => props.modelValue,
      (newVal) => {
        photos.value = [...newVal]
      }
    )

    const triggerFileSelect = () => {
      if (uploading.value) return
      fileInputRef.value?.click()
    }

    const uploadBatch = async (files: File[]): Promise<{ success: string[]; failed: { filename: string; error: string }[] }> => {
      const formData = new FormData()
      files.forEach((file) => {
        formData.append('files', file)
      })
      try {
        const response = await request.post('/upload/batch', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
        if (response.code === 200 && response.data) {
          const data = response.data as { success?: { url: string }[]; failed?: { filename: string; error: string }[] }
          const successUrls: string[] = (data.success || []).map((item) => item.url)
          const failedItems: { filename: string; error: string }[] = (data.failed || []).map((item) => ({
            filename: item.filename || '未知文件',
            error: item.error || '上传失败',
          }))
          return { success: successUrls, failed: failedItems }
        }
        return { success: [], failed: files.map((f) => ({ filename: f.name, error: response.message || '上传失败' })) }
      } catch (error: any) {
        return { success: [], failed: files.map((f) => ({ filename: f.name, error: error.message || '网络错误' })) }
      }
    }

    const handleFileSelect = async (event: Event) => {
      const target = event.target as HTMLInputElement
      const files = target.files
      if (!files || files.length === 0) return

      const remaining = props.maxCount - photos.value.length
      if (remaining <= 0) {
        ElMessage.warning('已达到最大上传数量')
        target.value = ''
        return
      }
      const filesToProcess = Array.from(files).slice(0, remaining)

      if (files.length > remaining) {
        ElMessage.info(`最多还能上传${remaining}张图片，已自动截取前${remaining}张`)
      }

      const oversizedFiles: File[] = []
      const validFiles: File[] = []
      for (const file of filesToProcess) {
        if (file.size > props.maxSize) {
          oversizedFiles.push(file)
        } else {
          validFiles.push(file)
        }
      }

      for (const file of oversizedFiles) {
        ElMessage.warning(`图片 ${file.name} 大小不能超过 ${props.maxSize / 1024 / 1024}MB`)
      }

      if (validFiles.length === 0) {
        target.value = ''
        return
      }

      uploading.value = true

      const { success, failed } = await uploadBatch(validFiles)

      if (success.length > 0) {
        photos.value.push(...success)
      }

      for (const item of failed) {
        ElMessage.error(`${item.filename} 上传失败: ${item.error}`)
      }

      uploading.value = false
      emit('update:modelValue', [...photos.value])
      target.value = ''

      if (success.length > 0 && failed.length > 0) {
        ElMessage.warning(`成功上传${success.length}张图片，${failed.length}张失败`)
      } else if (success.length > 0) {
        ElMessage.success(`成功上传${success.length}张图片`)
      }
    }

    const removePhoto = async (index: number) => {
      try {
        await ElMessageBox.confirm('是否要删除该图片？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        })
        photos.value.splice(index, 1)
        emit('update:modelValue', [...photos.value])
      } catch {
        // cancelled
      }
    }

    const previewPhoto = (photo: string) => {
      window.open(photo, '_blank')
    }

    return {
      photos,
      fileInputRef,
      uploading,
      triggerFileSelect,
      handleFileSelect,
      removePhoto,
      previewPhoto,
    }
  },
})
</script>

<style scoped>
.photo-upload {
  width: 100%;
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.photo-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--color-border);
  cursor: pointer;
}

.photo-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.delete-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.6);
  color: var(--color-bg-card);
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.delete-btn:hover {
  background: var(--color-danger);
}

.photo-add {
  aspect-ratio: 1;
  border: 2px dashed #d0d7de;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.add-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-text-secondary);
  padding: 16px;
}

.add-btn:hover {
  color: var(--color-primary);
}

.add-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.add-icon {
  font-size: 32px;
  font-weight: 300;
  line-height: 1;
}

.add-text {
  font-size: 12px;
}

.photo-tip {
  margin-top: 8px;
  font-size: 12px;
  color: var(--color-text-placeholder);
}
</style>
