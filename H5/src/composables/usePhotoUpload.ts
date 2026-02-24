/**
 * 图片上传组合式函数
 * 统一管理图片拍照、处理、上传逻辑
 */
import { ref } from 'vue'
import { showLoadingToast, closeToast, showSuccessToast, showFailToast, showConfirmDialog } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import { processPhoto, getCurrentLocation } from '../utils/watermark'
import { userStore } from '../stores/userStore'

interface PhotoUploadOptions {
  maxPhotos?: number
  endpoint?: string
}

/**
 * 图片上传组合式函数
 * @param options 配置选项
 * @returns 图片上传相关的状态和方法
 */
export const usePhotoUpload = (options: PhotoUploadOptions = {}) => {
  const { maxPhotos = 9, endpoint = '/upload' } = options
  
  const photos = ref<string[]>([])
  const showPopup = ref(false)

  /**
   * 初始化图片列表
   * @param photoData 图片数据（字符串或数组）
   */
  const initPhotos = (photoData: string | string[] | null | undefined) => {
    if (!photoData) {
      photos.value = []
      return
    }
    try {
      photos.value = typeof photoData === 'string' ? JSON.parse(photoData) : photoData
    } catch {
      photos.value = []
    }
  }

  /**
   * 打开图片弹窗
   */
  const openPhotoPopup = () => {
    showPopup.value = true
  }

  /**
   * 关闭图片弹窗
   */
  const closePhotoPopup = () => {
    showPopup.value = false
  }

  /**
   * 拍照并上传
   */
  const capturePhoto = async () => {
    if (photos.value.length >= maxPhotos) {
      showFailToast(`最多上传${maxPhotos}张图片`)
      return
    }

    const input = document.createElement('input')
    input.type = 'file'
    input.accept = 'image/*'
    input.capture = 'environment'
    
    input.onchange = async (e: Event) => {
      const target = e.target as HTMLInputElement
      const file = target.files?.[0]
      if (!file) return
      
      showLoadingToast({ message: '处理中...', forbidClick: true })
      
      try {
        const userName = userStore.getUser()?.name || '未知用户'
        const location = await getCurrentLocation()
        const processedFile = await processPhoto(file, {
          userName,
          includeLocation: true,
          latitude: location?.latitude,
          longitude: location?.longitude
        })
        
        const formDataObj = new FormData()
        formDataObj.append('file', processedFile)
        
        const response = await api.post<unknown, ApiResponse<{ url: string }>>(endpoint, formDataObj, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        
        if (response.code === 200 && response.data) {
          photos.value.push(response.data.url)
          showSuccessToast('上传成功')
        }
      } catch (error) {
        console.error('Failed to upload photo:', error)
        showFailToast('上传失败')
      } finally {
        closeToast()
      }
    }
    
    input.click()
  }

  /**
   * 删除图片
   * @param index 图片索引
   */
  const removePhoto = async (index: number) => {
    try {
      await showConfirmDialog({
        title: '提示',
        message: '是否要删除，新增的图片会重新打水印'
      })
      photos.value.splice(index, 1)
    } catch {
    }
  }

  /**
   * 获取图片JSON字符串
   * @returns 图片数组的JSON字符串
   */
  const getPhotosJson = (): string => {
    return JSON.stringify(photos.value)
  }

  /**
   * 清空图片
   */
  const clearPhotos = () => {
    photos.value = []
  }

  return {
    photos,
    showPopup,
    initPhotos,
    openPhotoPopup,
    closePhotoPopup,
    capturePhoto,
    removePhoto,
    getPhotosJson,
    clearPhotos
  }
}
