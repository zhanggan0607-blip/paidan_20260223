import { formatDateTime as _formatDateTime } from './format'

export interface WatermarkOptions {
  userName: string
  includeLocation?: boolean
  latitude?: number | null
  longitude?: number | null
  maxSizeKB?: number
  maxDimension?: number
}

const formatDateTime = (): string => _formatDateTime(new Date())

const formatLocation = (lat: number, lng: number): string => {
  const latDir = lat >= 0 ? 'N' : 'S'
  const lngDir = lng >= 0 ? 'E' : 'W'
  return `${Math.abs(lat).toFixed(6)}°${latDir} ${Math.abs(lng).toFixed(6)}°${lngDir}`
}

function withTimeout<T>(promise: Promise<T>, ms: number, errorMessage: string): Promise<T> {
  return Promise.race([
    promise,
    new Promise<never>((_, reject) =>
      setTimeout(() => reject(new Error(errorMessage)), ms)
    ),
  ])
}

async function loadImage(file: File): Promise<HTMLImageElement> {
  if (typeof createImageBitmap === 'function') {
    try {
      const bitmap = await createImageBitmap(file)
      const canvas = document.createElement('canvas')
      canvas.width = bitmap.width
      canvas.height = bitmap.height
      const ctx = canvas.getContext('2d')!
      ctx.drawImage(bitmap, 0, 0)
      bitmap.close()

      const img = new Image()
      return new Promise((resolve, reject) => {
        img.onload = () => resolve(img)
        img.onerror = () => reject(new Error('图片加载失败'))
        img.src = canvas.toDataURL('image/jpeg')
      })
    } catch {
      // fallthrough to FileReader
    }
  }

  return new Promise((resolve, reject) => {
    const img = new Image()
    const reader = new FileReader()
    img.onload = () => resolve(img)
    img.onerror = () => reject(new Error('图片加载失败'))
    reader.onload = (e) => { img.src = e.target?.result as string }
    reader.onerror = () => reject(new Error('文件读取失败'))
    reader.readAsDataURL(file)
  })
}

function drawWatermark(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  options: WatermarkOptions
): void {
  const lines: string[] = [`${options.userName} ${formatDateTime()}`]

  if (options.includeLocation && options.latitude && options.longitude) {
    lines.push(formatLocation(options.latitude, options.longitude))
  }

  const fontSize = Math.max(14, Math.floor(width / 30))
  ctx.font = `bold ${fontSize}px Arial`
  ctx.textAlign = 'left'
  ctx.textBaseline = 'bottom'

  const padding = fontSize
  const lineHeight = fontSize * 1.3
  const totalHeight = lines.length * lineHeight

  let maxTextWidth = 0
  lines.forEach(line => {
    const metrics = ctx.measureText(line)
    if (metrics.width > maxTextWidth) {
      maxTextWidth = metrics.width
    }
  })

  const bgX = padding
  const bgY = height - padding - totalHeight - 8
  const bgWidth = maxTextWidth + 16
  const bgHeight = totalHeight + 8

  ctx.fillStyle = 'rgba(0, 0, 0, 0.5)'
  ctx.fillRect(bgX, bgY, bgWidth, bgHeight)

  ctx.fillStyle = '#FFFFFF'
  lines.forEach((line, index) => {
    const y = height - padding - 4 - (lines.length - 1 - index) * lineHeight
    ctx.fillText(line, padding + 8, y)
  })
}

function compressCanvas(
  canvas: HTMLCanvasElement,
  maxSizeBytes: number
): Promise<Blob> {
  return new Promise((resolve, reject) => {
    const tryQuality = (hi: number, lo: number): void => {
      const q = (hi + lo) / 2
      canvas.toBlob((blob) => {
        if (!blob) {
          reject(new Error('图片压缩失败'))
          return
        }
        if (hi - lo < 0.05) {
          resolve(blob)
          return
        }
        if (blob.size <= maxSizeBytes) {
          if (hi - lo < 0.1 || q >= 0.85) {
            resolve(blob)
          } else {
            tryQuality(hi, q)
          }
        } else {
          tryQuality(q, lo)
        }
      }, 'image/jpeg', Math.max(0.1, Math.min(q, 0.95)))
    }

    canvas.toBlob((blob) => {
      if (!blob) {
        reject(new Error('图片压缩失败'))
        return
      }
      if (blob.size <= maxSizeBytes) {
        resolve(blob)
        return
      }
      tryQuality(0.9, 0.1)
    }, 'image/jpeg', 0.85)
  })
}

export const addWatermark = (
  file: File,
  options: WatermarkOptions
): Promise<Blob> => {
  return new Promise((resolve, reject) => {
    const maxDimension = options.maxDimension || 1280

    loadImage(file).then(img => {
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')

      if (!ctx) {
        reject(new Error('无法创建Canvas上下文'))
        return
      }

      let width = img.width
      let height = img.height

      if (width > maxDimension || height > maxDimension) {
        if (width > height) {
          height = Math.floor((height * maxDimension) / width)
          width = maxDimension
        } else {
          width = Math.floor((width * maxDimension) / height)
          height = maxDimension
        }
      }

      canvas.width = width
      canvas.height = height

      ctx.drawImage(img, 0, 0, width, height)
      drawWatermark(ctx, width, height, options)

      canvas.toBlob((blob) => {
        if (blob) {
          resolve(blob)
        } else {
          reject(new Error('图片处理失败'))
        }
      }, 'image/jpeg', 0.85)
    }).catch(reject)
  })
}

export const blobToFile = (blob: Blob, fileName: string): File => {
  return new File([blob], fileName, { type: blob.type || 'image/jpeg' })
}

export const compressImage = (file: File, maxSizeKB: number = 500): Promise<Blob> => {
  return new Promise((resolve, reject) => {
    loadImage(file).then(img => {
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')

      if (!ctx) {
        reject(new Error('无法创建Canvas上下文'))
        return
      }

      let width = img.width
      let height = img.height
      const maxDimension = 1280

      if (width > maxDimension || height > maxDimension) {
        if (width > height) {
          height = Math.floor((height * maxDimension) / width)
          width = maxDimension
        } else {
          width = Math.floor((width * maxDimension) / height)
          height = maxDimension
        }
      }

      canvas.width = width
      canvas.height = height
      ctx.drawImage(img, 0, 0, width, height)

      compressCanvas(canvas, maxSizeKB * 1024).then(resolve).catch(reject)
    }).catch(reject)
  })
}

export const processPhoto = async (
  file: File,
  options: WatermarkOptions | string
): Promise<File> => {
  const watermarkOptions: WatermarkOptions = typeof options === 'string'
    ? { userName: options }
    : options

  const maxDimension = watermarkOptions.maxDimension || 1280
  const maxSizeKB = watermarkOptions.maxSizeKB || 500

  const result = await withTimeout(
    (async () => {
      const img = await loadImage(file)

      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')

      if (!ctx) {
        throw new Error('无法创建Canvas上下文')
      }

      let width = img.width
      let height = img.height

      if (width > maxDimension || height > maxDimension) {
        if (width > height) {
          height = Math.floor((height * maxDimension) / width)
          width = maxDimension
        } else {
          width = Math.floor((width * maxDimension) / height)
          height = maxDimension
        }
      }

      canvas.width = width
      canvas.height = height

      ctx.drawImage(img, 0, 0, width, height)
      drawWatermark(ctx, width, height, watermarkOptions)

      const blob = await compressCanvas(canvas, maxSizeKB * 1024)
      return blobToFile(blob, file.name)
    })(),
    15000,
    '图片处理超时，请重试'
  )

  return result
}

export const getCurrentLocation = (): Promise<{ latitude: number; longitude: number } | null> => {
  return new Promise((resolve) => {
    if (!navigator.geolocation) {
      resolve(null)
      return
    }

    let resolved = false
    const done = (value: { latitude: number; longitude: number } | null) => {
      if (!resolved) {
        resolved = true
        resolve(value)
      }
    }

    setTimeout(() => done(null), 5000)

    navigator.geolocation.getCurrentPosition(
      (position) => {
        done({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude
        })
      },
      () => {
        done(null)
      },
      {
        enableHighAccuracy: false,
        timeout: 3000,
        maximumAge: 60000
      }
    )
  })
}
