"""
文件服务API
从数据库读取上传的文件，确保数据永久保存在阿里云RDS
"""
import os
from io import BytesIO
from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.uploaded_file import UploadedFile
from app.utils.logging_config import get_logger
from app.utils import get_inline_content_disposition

logger = get_logger(__name__)

router = APIRouter(prefix="/files", tags=["File Service"])

UPLOAD_DIR = "/app/uploads"

THUMBNAIL_CACHE = {}
THUMBNAIL_MAX_CACHE_SIZE = 100

def generate_thumbnail(image_data: bytes, size: int = 200) -> bytes:
    """
    生成缩略图
    
    Args:
        image_data: 原始图片数据
        size: 缩略图尺寸（正方形）
        
    Returns:
        缩略图数据
    """
    try:
        from PIL import Image
        
        img = Image.open(BytesIO(image_data))
        
        width, height = img.size
        left = (width - min(width, height)) // 2
        top = (height - min(width, height)) // 2
        right = left + min(width, height)
        bottom = top + min(width, height)
        img = img.crop((left, top, right, bottom))
        
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        
        output = BytesIO()
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        img.save(output, format='JPEG', quality=85, optimize=True)
        
        return output.getvalue()
    except Exception as e:
        logger.error(f"生成缩略图失败: {e}")
        return image_data


@router.get("/{upload_date}/{filename}")
async def get_file(
    upload_date: str,
    filename: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    从数据库获取文件
    
    首先尝试从数据库读取文件，如果不存在则尝试从文件系统读取（兼容旧数据）
    
    Args:
        upload_date: 上传日期(YYYYMMDD)
        filename: 文件名
        request: FastAPI请求对象
        db: 数据库会话
        
    Returns:
        StreamingResponse: 文件流响应
    """
    file_path = f"/uploads/{upload_date}/{filename}"
    
    uploaded_file = db.query(UploadedFile).filter(
        UploadedFile.file_path == file_path
    ).first()
    
    if uploaded_file:
        logger.info(f"从数据库读取文件: {file_path}")
        
        media_type = uploaded_file.content_type or "application/octet-stream"
        
        return StreamingResponse(
            BytesIO(uploaded_file.file_data),
            media_type=media_type,
            headers={
                "Cache-Control": "public, max-age=31536000",
                "Content-Disposition": get_inline_content_disposition(uploaded_file.original_filename or filename)
            }
        )
    
    file_system_path = os.path.join(UPLOAD_DIR, upload_date, filename)
    if os.path.exists(file_system_path):
        logger.info(f"从文件系统读取文件(兼容旧数据): {file_path}")
        
        content_type = "image/jpeg"
        if filename.lower().endswith(".png"):
            content_type = "image/png"
        elif filename.lower().endswith(".gif"):
            content_type = "image/gif"
        elif filename.lower().endswith(".webp"):
            content_type = "image/webp"
        
        def file_iterator():
            with open(file_system_path, "rb") as f:
                while chunk := f.read(65536):
                    yield chunk
        
        return StreamingResponse(
            file_iterator(),
            media_type=content_type,
            headers={
                "Cache-Control": "public, max-age=31536000",
                "Content-Disposition": get_inline_content_disposition(filename)
            }
        )
    
    logger.warning(f"文件不存在: {file_path}")
    raise HTTPException(status_code=404, detail="文件不存在")


@router.get("/by-id/{file_id}")
async def get_file_by_id(
    file_id: str,
    db: Session = Depends(get_db)
):
    """
    通过文件ID获取文件
    
    Args:
        file_id: 文件唯一标识UUID
        db: 数据库会话
        
    Returns:
        StreamingResponse: 文件流响应
    """
    uploaded_file = db.query(UploadedFile).filter(
        UploadedFile.file_id == file_id
    ).first()
    
    if not uploaded_file:
        logger.warning(f"文件不存在: file_id={file_id}")
        raise HTTPException(status_code=404, detail="文件不存在")
    
    logger.info(f"通过ID从数据库读取文件: file_id={file_id}")
    
    media_type = uploaded_file.content_type or "application/octet-stream"
    
    return StreamingResponse(
        BytesIO(uploaded_file.file_data),
        media_type=media_type,
        headers={
            "Cache-Control": "public, max-age=31536000",
            "Content-Disposition": get_inline_content_disposition(uploaded_file.original_filename or uploaded_file.stored_filename)
        }
    )


@router.get("/thumbnail/{upload_date}/{filename}")
async def get_thumbnail(
    upload_date: str,
    filename: str,
    size: int = Query(200, ge=50, le=500, description="缩略图尺寸"),
    db: Session = Depends(get_db)
):
    """
    获取图片缩略图
    
    生成正方形缩略图，取图片中间部分裁剪
    
    Args:
        upload_date: 上传日期(YYYYMMDD)
        filename: 文件名
        size: 缩略图尺寸（默认200px）
        db: 数据库会话
        
    Returns:
        StreamingResponse: 缩略图流响应
    """
    file_path = f"/uploads/{upload_date}/{filename}"
    
    cache_key = f"{file_path}_{size}"
    if cache_key in THUMBNAIL_CACHE:
        logger.info(f"从缓存返回缩略图: {cache_key}")
        return StreamingResponse(
            BytesIO(THUMBNAIL_CACHE[cache_key]),
            media_type="image/jpeg",
            headers={
                "Cache-Control": "public, max-age=31536000",
                "Content-Disposition": get_inline_content_disposition(f"thumb_{filename}")
            }
        )
    
    uploaded_file = db.query(UploadedFile).filter(
        UploadedFile.file_path == file_path
    ).first()
    
    if not uploaded_file:
        file_system_path = os.path.join(UPLOAD_DIR, upload_date, filename)
        if os.path.exists(file_system_path):
            with open(file_system_path, "rb") as f:
                image_data = f.read()
        else:
            raise HTTPException(status_code=404, detail="文件不存在")
    else:
        image_data = uploaded_file.file_data
    
    thumbnail_data = generate_thumbnail(image_data, size)
    
    if len(THUMBNAIL_CACHE) >= THUMBNAIL_MAX_CACHE_SIZE:
        oldest_key = next(iter(THUMBNAIL_CACHE))
        del THUMBNAIL_CACHE[oldest_key]
    
    THUMBNAIL_CACHE[cache_key] = thumbnail_data
    
    logger.info(f"生成并返回缩略图: {cache_key}")
    
    return StreamingResponse(
        BytesIO(thumbnail_data),
        media_type="image/jpeg",
        headers={
            "Cache-Control": "public, max-age=31536000",
            "Content-Disposition": get_inline_content_disposition(f"thumb_{filename}")
        }
    )
