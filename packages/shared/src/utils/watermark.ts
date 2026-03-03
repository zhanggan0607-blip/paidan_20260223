/**
 * 图片水印工具
 * 为拍照上传的图片添加用户名、时间和经纬度水印
 */

export interface WatermarkOptions {
  userName: string
  includeLocation?: boolean
  latitude?: number | null
  longitude?: number | null
  maxSizeKB?: number
}

/**
 * 获取当前格式化时间
 * @returns 格式化后的时间字符串 YYYY-MM-DD HH:mm:ss
 */
const formatDateTime = (): string => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

/**
 * 格式化经纬度
 * @param lat 纬度
 * @param lng 经度
 * @returns 格式化后的经纬度字符串
 */
const formatLocation = (lat: number, lng: number): string => {
  const latDir = lat >= 0 ? 'N' : 'S'
  const lngDir = lng >= 0 ? 'E' : 'W'
  return `${Math.abs(lat).toFixed(6)}°${latDir} ${Math.abs(lng).toFixed(6)}°${lngDir}`
}

/**
 * 为图片添加水印
 * @param file 原始图片文件
 * @param options 水印选项
 * @returns 添加水印后的Blob对象
 */
export const addWatermark = (
  file: File, 
  options: WatermarkOptions
): Promise<Blob> => {
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
      
      canvas.width = img.width
      canvas.height = img.height
      
      ctx.drawImage(img, 0, 0)
      
      const lines: string[] = [`${options.userName} ${formatDateTime()}`]
      
      if (options.includeLocation && options.latitude && options.longitude) {
        lines.push(formatLocation(options.latitude, options.longitude))
      }
      
      const fontSize = Math.max(16, Math.floor(img.width / 30))
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
      const bgY = canvas.height - padding - totalHeight - 8
      const bgWidth = maxTextWidth + 16
      const bgHeight = totalHeight + 8
      
      ctx.fillStyle = 'rgba(0, 0, 0, 0.5)'
      ctx.fillRect(bgX, bgY, bgWidth, bgHeight)
      
      ctx.fillStyle = '#FFFFFF'
      lines.forEach((line, index) => {
        const y = canvas.height - padding - 4 - (lines.length - 1 - index) * lineHeight
        ctx.fillText(line, padding + 8, y)
      })
      
      canvas.toBlob((blob) => {
        if (blob) {
          resolve(blob)
        } else {
          reject(new Error('图片处理失败'))
        }
      }, 'image/jpeg', 0.9)
    }
    
    img.onerror = () => {
      URL.revokeObjectURL(url)
      reject(new Error('图片加载失败'))
    }
    
    img.src = url
  })
}

/**
 * 将Blob转换为File对象
 * @param blob Blob对象
 * @param fileName 文件名
 * @returns File对象
 */
export const blobToFile = (blob: Blob, fileName: string): File => {
  return new File([blob], fileName, { type: blob.type || 'image/jpeg' })
}

/**
 * 压缩图片到指定大小
 * @param file 原始图片文件
 * @param maxSizeKB 最大大小(KB)，默认500KB
 * @returns 压缩后的Blob对象
 */
export const compressImage = (file: File, maxSizeKB: number = 500): Promise<Blob> => {
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
      const maxDimension = 1920
      
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
      
      let quality = 0.9
      const maxSizeBytes = maxSizeKB * 1024
      
      const compress = (q: number): void => {
        canvas.toBlob((blob) => {
          if (blob) {
            if (blob.size <= maxSizeBytes || q <= 0.1) {
              resolve(blob)
            } else {
              compress(q - 0.1)
            }
          } else {
            reject(new Error('图片压缩失败'))
          }
        }, 'image/jpeg', q)
      }
      
      compress(quality)
    }
    
    img.onerror = () => {
      URL.revokeObjectURL(url)
      reject(new Error('图片加载失败'))
    }
    
    img.src = url
  })
}

/**
 * 生成正方形缩略图
 * @param file 原始图片文件
 * @param size 缩略图尺寸，默认200px
 * @returns 缩略图Blob对象
 */
export const generateThumbnail = (file: File, size: number = 200): Promise<Blob> => {
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
      
      const minDimension = Math.min(img.width, img.height)
      const sx = (img.width - minDimension) / 2
      const sy = (img.height - minDimension) / 2
      
      canvas.width = size
      canvas.height = size
      
      ctx.drawImage(img, sx, sy, minDimension, minDimension, 0, 0, size, size)
      
      canvas.toBlob((blob) => {
        if (blob) {
          resolve(blob)
        } else {
          reject(new Error('缩略图生成失败'))
        }
      }, 'image/jpeg', 0.8)
    }
    
    img.onerror = () => {
      URL.revokeObjectURL(url)
      reject(new Error('图片加载失败'))
    }
    
    img.src = url
  })
}

/**
 * 处理拍照图片：添加水印并压缩
 * @param file 原始图片文件
 * @param options 水印选项
 * @returns 处理后的File对象
 */
export const processPhoto = async (
  file: File, 
  options: WatermarkOptions | string
): Promise<File> => {
  const watermarkOptions: WatermarkOptions = typeof options === 'string' 
    ? { userName: options } 
    : options
  
  const watermarkedBlob = await addWatermark(file, watermarkOptions)
  const maxSizeKB = watermarkOptions.maxSizeKB || 500
  const compressedBlob = await compressImage(blobToFile(watermarkedBlob, file.name), maxSizeKB)
  return blobToFile(compressedBlob, file.name)
}

/**
 * 获取当前位置
 * @returns 位置信息或null
 */
export const getCurrentLocation = (): Promise<{ latitude: number; longitude: number } | null> => {
  return new Promise((resolve) => {
    if (!navigator.geolocation) {
      resolve(null)
      return
    }
    
    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude
        })
      },
      () => {
        resolve(null)
      },
      {
        enableHighAccuracy: true,
        timeout: 5000,
        maximumAge: 0
      }
    )
  })
}
