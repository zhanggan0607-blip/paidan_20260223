import { ref, type Ref } from 'vue'
import { showImagePreview, showToast } from 'vant'
import { processPhoto, getCurrentLocation } from '@sstcp/shared/utils/watermark'

const MAX_PHOTOS = 9
const COMPRESS_THRESHOLD_KB = 500
const MAX_IMAGE_DIMENSION = 1920
const COMPRESS_QUALITY_HIGH = 0.9
const COMPRESS_QUALITY_LOW = 0.1

const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent)
const isDingTalk = /DingTalk/i.test(navigator.userAgent)
const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent)
const useBase64Upload = isIOS || isDingTalk

interface PhotoItem {
  url: string
  name?: string
  isExisting?: boolean
}

export function usePhotoUpload(photos: Ref<PhotoItem[]>, userName: string) {
  const uploading = ref(false)
  const uploadError = ref<string | null>(null)

  async function compressImage(file: File): Promise<Blob> {
    return new Promise((resolve, reject) => {
      const img = new Image()
      const url = URL.createObjectURL(file)

      img.onload = () => {
        URL.revokeObjectURL(url)
        const canvas = document.createElement('canvas')
        const ctx = canvas.getContext('2d')
        if (!ctx) {
          reject(new Error('无法创建Canvas上下文'))
          return
        }

        let width = img.width
        let height = img.height
        if (width > MAX_IMAGE_DIMENSION || height > MAX_IMAGE_DIMENSION) {
          if (width > height) {
            height = Math.floor((height * MAX_IMAGE_DIMENSION) / width)
            width = MAX_IMAGE_DIMENSION
          } else {
            width = Math.floor((width * MAX_IMAGE_DIMENSION) / height)
            height = MAX_IMAGE_DIMENSION
          }
        }

        canvas.width = width
        canvas.height = height
        ctx.drawImage(img, 0, 0, width, height)

        const maxSizeBytes = COMPRESS_THRESHOLD_KB * 1024
        const compress = (q: number): void => {
          canvas.toBlob(
            (blob) => {
              if (blob) {
                if (blob.size <= maxSizeBytes || q <= COMPRESS_QUALITY_LOW) {
                  resolve(blob)
                } else {
                  compress(q - 0.1)
                }
              } else {
                reject(new Error('图片压缩失败'))
              }
            },
            'image/jpeg',
            q
          )
        }
        compress(COMPRESS_QUALITY_HIGH)
      }

      img.onerror = () => {
        URL.revokeObjectURL(url)
        reject(new Error('图片加载失败'))
      }
      img.src = url
    })
  }

  async function handlePhotoCapture(event: Event): Promise<void> {
    const input = event.target as HTMLInputElement
    if (!input.files || input.files.length === 0) return

    if (photos.value.length >= MAX_PHOTOS) {
      showToast(`最多上传${MAX_PHOTOS}张照片`)
      return
    }

    uploading.value = true
    uploadError.value = null

    try {
      const file = input.files[0]
      let processedFile: File

      try {
        const location = await getCurrentLocation()
        processedFile = await processPhoto(file, {
          userName,
          includeLocation: !!location,
          latitude: location?.latitude,
          longitude: location?.longitude,
          maxSizeKB: COMPRESS_THRESHOLD_KB
        })
      } catch {
        const compressedBlob = await compressImage(file)
        processedFile = new File([compressedBlob], file.name, { type: 'image/jpeg' })
      }

      const url = URL.createObjectURL(processedFile)
      photos.value.push({
        url,
        name: processedFile.name
      })
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : '图片处理失败'
      uploadError.value = msg
      showToast(msg)
    } finally {
      uploading.value = false
      input.value = ''
    }
  }

  async function tryCaptureOnIOS(): Promise<void> {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = 'image/*'
    input.capture = 'environment'
    input.onchange = (e: Event) => handlePhotoCapture(e)
    input.click()
  }

  function handleRemovePhoto(index: number): void {
    const photo = photos.value[index]
    if (photo && photo.url && !photo.isExisting) {
      URL.revokeObjectURL(photo.url)
    }
    photos.value.splice(index, 1)
  }

  function getFullImageUrl(url: string): string {
    if (!url) return ''
    if (url.startsWith('blob:') || url.startsWith('data:') || url.startsWith('http')) {
      return url
    }
    return `${window.location.origin}/api/v1${url.startsWith('/') ? '' : '/'}${url}`
  }

  function handlePreviewPhoto(index: number): void {
    const urls = photos.value.map((p) => getFullImageUrl(p.url))
    showImagePreview({
      images: urls,
      startPosition: index
    })
  }

  async function handlePhotoSave(
    saveFn: (formData: FormData) => Promise<unknown>,
    getFormData: () => FormData
  ): Promise<boolean> {
    uploading.value = true
    uploadError.value = null
    try {
      const formData = getFormData()
      await saveFn(formData)
      showToast('保存成功')
      return true
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : '保存失败'
      uploadError.value = msg
      showToast(msg)
      return false
    } finally {
      uploading.value = false
    }
  }

  return {
    uploading,
    uploadError,
    compressImage,
    handlePhotoCapture,
    tryCaptureOnIOS,
    handleRemovePhoto,
    getFullImageUrl,
    handlePreviewPhoto,
    handlePhotoSave,
    MAX_PHOTOS,
    isIOS,
    isDingTalk,
    isMobile,
    useBase64Upload
  }
}
