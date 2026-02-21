/**
 * 图片水印工具
 * 为拍照上传的图片添加用户名和时间水印
 */

// TODO: 水印工具 - 考虑加入经纬度信息(需要获取GPS权限)
// FIXME: 水印位置目前固定在右下角，应该支持配置
// TODO: 考虑加入防篡改水印(如数字签名)

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
 * 为图片添加水印
 * @param file 原始图片文件
 * @param userName 用户名
 * @returns 添加水印后的Blob对象
 */
export const addWatermark = (file: File, userName: string): Promise<Blob> => {
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
      
      const watermarkText = `${userName} ${formatDateTime()}`
      
      const fontSize = Math.max(16, Math.floor(img.width / 30))
      ctx.font = `bold ${fontSize}px Arial`
      ctx.textAlign = 'left'
      ctx.textBaseline = 'bottom'
      
      const padding = fontSize
      const textMetrics = ctx.measureText(watermarkText)
      const textWidth = textMetrics.width
      const textHeight = fontSize
      
      const bgX = padding
      const bgY = canvas.height - padding - textHeight - 8
      const bgWidth = textWidth + 16
      const bgHeight = textHeight + 8
      
      ctx.fillStyle = 'rgba(0, 0, 0, 0.5)'
      ctx.fillRect(bgX, bgY, bgWidth, bgHeight)
      
      ctx.fillStyle = '#FFFFFF'
      ctx.fillText(watermarkText, padding + 8, canvas.height - padding - 4)
      
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
 * 处理拍照图片：添加水印并压缩
 * @param file 原始图片文件
 * @param userName 用户名
 * @param maxSizeKB 最大大小(KB)，默认500KB
 * @returns 处理后的File对象
 */
export const processPhoto = async (
  file: File, 
  userName: string, 
  maxSizeKB: number = 500
): Promise<File> => {
  const watermarkedBlob = await addWatermark(file, userName)
  const compressedBlob = await compressImage(blobToFile(watermarkedBlob, file.name), maxSizeKB)
  return blobToFile(compressedBlob, file.name)
}
