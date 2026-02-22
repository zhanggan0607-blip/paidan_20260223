"""
文件验证工具模块
提供文件内容验证、图片类型检测等功能
"""
import imghdr
import hashlib
from typing import Optional, Tuple
from fastapi import HTTPException, status


ALLOWED_IMAGE_TYPES = ['jpeg', 'png', 'gif', 'webp']
ALLOWED_MIME_TYPES = {
    'image/jpeg': 'jpeg',
    'image/png': 'png',
    'image/gif': 'gif',
    'image/webp': 'webp'
}
MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_FILENAME_LENGTH = 255


def validate_image_content(content: bytes, declared_content_type: str = None) -> Tuple[bool, Optional[str]]:
    """
    验证图片文件内容是否合法
    
    Args:
        content: 文件二进制内容
        declared_content_type: 声明的Content-Type
        
    Returns:
        Tuple[bool, Optional[str]]: (是否合法, 实际图片类型)
    """
    if len(content) == 0:
        return False, None
    
    image_type = imghdr.what(None, h=content)
    
    if image_type is None:
        return False, None
    
    if image_type not in ALLOWED_IMAGE_TYPES:
        return False, image_type
    
    if declared_content_type:
        expected_type = ALLOWED_MIME_TYPES.get(declared_content_type)
        if expected_type and expected_type != image_type:
            return False, image_type
    
    return True, image_type


def validate_file_size(content: bytes, max_size: int = MAX_FILE_SIZE) -> bool:
    """
    验证文件大小是否在限制范围内
    
    Args:
        content: 文件二进制内容
        max_size: 最大文件大小（字节）
        
    Returns:
        bool: 文件大小是否合法
    """
    return len(content) <= max_size


def calculate_file_hash(content: bytes) -> str:
    """
    计算文件的SHA256哈希值
    
    Args:
        content: 文件二进制内容
        
    Returns:
        str: 文件的SHA256哈希值
    """
    return hashlib.sha256(content).hexdigest()


def validate_filename(filename: str) -> bool:
    """
    验证文件名是否合法
    
    Args:
        filename: 文件名
        
    Returns:
        bool: 文件名是否合法
    """
    if not filename:
        return False
    
    if len(filename) > MAX_FILENAME_LENGTH:
        return False
    
    dangerous_chars = ['..', '/', '\\', '\x00']
    for char in dangerous_chars:
        if char in filename:
            return False
    
    return True


def get_file_extension(filename: str) -> str:
    """
    获取文件扩展名
    
    Args:
        filename: 文件名
        
    Returns:
        str: 文件扩展名（包含点号）
    """
    if '.' in filename:
        ext = filename.rsplit('.', 1)[-1].lower()
        return f'.{ext}'
    return '.jpg'


def validate_upload_file(content: bytes, filename: str, content_type: str = None) -> Tuple[bool, str]:
    """
    综合验证上传文件
    
    Args:
        content: 文件二进制内容
        filename: 文件名
        content_type: Content-Type
        
    Returns:
        Tuple[bool, str]: (是否合法, 错误信息或实际类型)
        
    Raises:
        HTTPException: 文件验证失败时抛出异常
    """
    if not validate_file_size(content):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制（最大{MAX_FILE_SIZE // 1024 // 1024}MB）"
        )
    
    if not validate_filename(filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件名不合法"
        )
    
    is_valid, actual_type = validate_image_content(content, content_type)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件内容验证失败，仅支持JPEG、PNG、GIF、WebP格式的图片"
        )
    
    if content_type and content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的文件类型，仅支持JPEG、PNG、GIF、WebP格式"
        )
    
    return True, actual_type
