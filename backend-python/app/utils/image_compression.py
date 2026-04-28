"""
图片压缩工具
使用Pillow库对上传的图片进行压缩优化
"""
import io
from PIL import Image
from typing import Tuple


def compress_image(
    image_data: bytes,
    quality: int = 85,
    max_size: Tuple[int, int] = (1920, 1920),
    convert_to_jpeg: bool = True
) -> Tuple[bytes, str]:
    """
    压缩图片
    
    Args:
        image_data: 原始图片数据
        quality: 压缩质量(1-100),默认85
        max_size: 最大尺寸(宽,高),默认1920x1920
        convert_to_jpeg: 是否转换为JPEG格式,默认True
    
    Returns:
        (压缩后的图片数据, 内容类型)
    """
    try:
        img = Image.open(io.BytesIO(image_data))
        
        if img.mode in ('RGBA', 'LA', 'P'):
            if convert_to_jpeg:
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            else:
                img = img.convert('RGBA')
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        output = io.BytesIO()
        
        if convert_to_jpeg:
            img.save(output, format='JPEG', quality=quality, optimize=True)
            content_type = 'image/jpeg'
        else:
            format_map = {
                'JPEG': 'JPEG',
                'PNG': 'PNG',
                'GIF': 'GIF',
                'WEBP': 'WEBP'
            }
            img_format = format_map.get(img.format, 'JPEG')
            
            if img_format == 'JPEG':
                img.save(output, format=img_format, quality=quality, optimize=True)
            elif img_format == 'PNG':
                img.save(output, format=img_format, optimize=True)
            else:
                img.save(output, format=img_format)
            
            content_type_map = {
                'JPEG': 'image/jpeg',
                'PNG': 'image/png',
                'GIF': 'image/gif',
                'WEBP': 'image/webp'
            }
            content_type = content_type_map.get(img_format, 'image/jpeg')
        
        compressed_data = output.getvalue()
        
        return compressed_data, content_type
        
    except Exception as e:
        raise ValueError(f"图片压缩失败: {str(e)}")


def get_image_info(image_data: bytes) -> dict:
    """
    获取图片信息
    
    Args:
        image_data: 图片数据
    
    Returns:
        包含图片信息的字典
    """
    try:
        img = Image.open(io.BytesIO(image_data))
        return {
            'format': img.format,
            'mode': img.mode,
            'size': img.size,
            'width': img.width,
            'height': img.height
        }
    except Exception as e:
        raise ValueError(f"获取图片信息失败: {str(e)}")
