import { showLoadingToast, closeToast, showFailToast, showConfirmDialog } from 'vant'
import { getCurrentLocation } from '@sstcp/shared'
import { uploadService } from '../services'

const isIOSDevice = () => {
  return /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)
}

interface CaptureOptions {
  userName: string
  latitude?: number
  longitude?: number
  onSuccess?: (url: string) => void
  onError?: (error: any) => void
}

export const useCameraCapture = () => {
  const processAndUpload = async (file: File, options: CaptureOptions): Promise<string | null> => {
    const { userName, latitude, longitude, onSuccess, onError } = options

    try {
      const location = await getCurrentLocation()
      const { processPhoto } = await import('@sstcp/shared')

      const processedFile = await processPhoto(file, {
        userName,
        includeLocation: true,
        latitude: location?.latitude ?? latitude,
        longitude: location?.longitude ?? longitude,
      })

      const response = await uploadService.uploadFile(processedFile)

      if (response.code === 200 && response.data) {
        if (onSuccess) {
          onSuccess(response.data.url)
        }
        return response.data.url
      } else {
        throw new Error(response.message || '上传失败')
      }
    } catch (error) {
      console.error('Upload failed:', error)
      if (onError) {
        onError(error)
      }
      throw error
    }
  }

  const captureWithAndroid = (onFileReady: (file: File) => void): (() => void) => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = 'image/*'
    input.capture = 'environment'

    input.onchange = (e: Event) => {
      const target = e.target as HTMLInputElement
      const file = target.files?.[0]
      if (file) {
        onFileReady(file)
      }
    }

    input.click()

    return () => {
      input.onchange = null
    }
  }

  const captureWithIOS = async (
    onFileReady: (file: File) => void,
    onCancel?: () => void
  ): Promise<void> => {
    showLoadingToast({ message: '正在打开相机...', forbidClick: true, duration: 0 })

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' }
      })

      closeToast()

      const video = document.createElement('video')
      video.srcObject = stream
      video.autoplay = true
      video.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;z-index:999999;object-fit:cover;background:#000;'

      const canvas = document.createElement('canvas')
      canvas.style.cssText = 'display:none;'

      document.body.appendChild(video)
      document.body.appendChild(canvas)

      video.play()

      const cleanup = () => {
        stream.getTracks().forEach(track => track.stop())
        if (document.body.contains(video)) {
          document.body.removeChild(video)
        }
        if (document.body.contains(canvas)) {
          document.body.removeChild(canvas)
        }
      }

      const capturePhoto = () => {
        cleanup()

        const videoWidth = video.videoWidth || 1280
        const videoHeight = video.videoHeight || 720
        canvas.width = videoWidth
        canvas.height = videoHeight

        const ctx = canvas.getContext('2d')
        if (ctx) {
          ctx.drawImage(video, 0, 0, videoWidth, videoHeight)
        }

        canvas.toBlob((blob) => {
          if (!blob) {
            showFailToast('拍照失败')
            return
          }

          const file = new File([blob], 'photo.jpg', { type: 'image/jpeg' })
          onFileReady(file)
        }, 'image/jpeg', 0.8)
      }

      setTimeout(() => {
        showConfirmDialog({
          title: '拍照',
          message: '准备好了吗？点击确认拍照',
          confirmButtonText: '拍照',
        }).then(() => {
          capturePhoto()
        }).catch(() => {
          cleanup()
          if (onCancel) {
            onCancel()
          }
        })
      }, 500)
    } catch (error: any) {
      closeToast()
      console.error('Camera error:', error)

      if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
        showFailToast('请允许使用相机权限')
      } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
        showFailToast('未找到相机设备')
      } else {
        showFailToast('相机打开失败')
      }

      if (onCancel) {
        onCancel()
      }
    }
  }

  const capture = async (options: CaptureOptions): Promise<string | null> => {
    const { userName, latitude, longitude, onSuccess, onError } = options

    return new Promise((resolve) => {
      const handleFile = async (file: File) => {
        showLoadingToast({ message: '处理中...', forbidClick: true })

        try {
          const url = await processAndUpload(file, {
            userName,
            latitude,
            longitude,
            onSuccess,
            onError,
          })
          resolve(url)
        } catch (error) {
          if (onError) {
            onError(error)
          }
          showFailToast('上传失败')
          resolve(null)
        } finally {
          closeToast()
        }
      }

      if (isIOSDevice()) {
        captureWithIOS(handleFile, () => resolve(null))
      } else {
        captureWithAndroid(handleFile)
      }
    })
  }

  return {
    capture,
    captureWithIOS,
    captureWithAndroid,
    processAndUpload,
  }
}
