<template>
  <div class="photo-upload">
    <div class="photo-grid">
      <div
        v-for="(photo, index) in photos"
        :key="index"
        class="photo-item"
      >
        <img :src="photo" alt="现场图片" loading="lazy" @click="previewPhoto(photo)" />
        <button class="delete-btn" @click.stop="removePhoto(index)" title="删除">×</button>
      </div>
      <div class="photo-add" v-if="photos.length < maxCount">
        <input
          ref="fileInputRef"
          type="file"
          accept="image/*"
          capture="environment"
          @change="handleFileSelect"
          style="display: none"
        />
        <button class="add-btn" @click="triggerFileSelect">
          <span class="add-icon">+</span>
          <span class="add-text">添加图片</span>
        </button>
      </div>
    </div>
    <div class="photo-tip">
      支持 jpg、png 格式，单张不超过 5MB，最多 {{ maxCount }} 张
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue'

export default defineComponent({
  name: 'PhotoUpload',
  props: {
    modelValue: {
      type: Array as () => string[],
      default: () => []
    },
    maxCount: {
      type: Number,
      default: 9
    },
    maxSize: {
      type: Number,
      default: 5 * 1024 * 1024
    }
  },
  emits: ['update:modelValue', 'upload'],
  setup(props, { emit }) {
    const photos = ref<string[]>([...props.modelValue])
    const fileInputRef = ref<HTMLInputElement | null>(null)

    watch(() => props.modelValue, (newVal) => {
      photos.value = [...newVal]
    })

    const triggerFileSelect = () => {
      fileInputRef.value?.click()
    }

    const handleFileSelect = async (event: Event) => {
      const target = event.target as HTMLInputElement
      const file = target.files?.[0]
      if (!file) return

      if (file.size > props.maxSize) {
        alert(`图片大小不能超过 ${props.maxSize / 1024 / 1024}MB`)
        target.value = ''
        return
      }

      const reader = new FileReader()
      reader.onload = (e) => {
        const dataUrl = e.target?.result as string
        photos.value.push(dataUrl)
        emit('update:modelValue', [...photos.value])
        emit('upload', dataUrl)
      }
      reader.readAsDataURL(file)
      target.value = ''
    }

    const removePhoto = (index: number) => {
      if (confirm('是否要删除该图片？')) {
        photos.value.splice(index, 1)
        emit('update:modelValue', [...photos.value])
      }
    }

    const previewPhoto = (photo: string) => {
      window.open(photo, '_blank')
    }

    return {
      photos,
      fileInputRef,
      triggerFileSelect,
      handleFileSelect,
      removePhoto,
      previewPhoto
    }
  }
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
  border: 1px solid #e0e0e0;
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
  color: #fff;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.delete-btn:hover {
  background: #f44336;
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
  color: #666;
  padding: 16px;
}

.add-btn:hover {
  color: #1976d2;
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
  color: #999;
}
</style>
