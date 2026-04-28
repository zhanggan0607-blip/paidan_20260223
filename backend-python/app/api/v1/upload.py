"""
文件上传API
优先将图片等文件存储到阿里云OSS，OSS不可用时降级到数据库存储
"""
import base64
import uuid
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user_required, UserInfo
from app.models.uploaded_file import UploadedFile
from app.schemas.common import ApiResponse
from app.utils.logging_config import get_logger
from app.utils.oss_service import get_oss_service, OSSService
from app.utils.image_compression import compress_image

logger = get_logger(__name__)
router = APIRouter(prefix="/upload", tags=["File Upload"])

ALLOWED_IMAGE_TYPES = {'jpeg', 'png', 'gif', 'webp'}
IMAGE_TYPE_TO_EXT = {
    'jpeg': 'jpg',
    'png': 'png',
    'gif': 'gif',
    'webp': 'webp'
}
IMAGE_TYPE_TO_MIME = {
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'webp': 'image/webp',
}
ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
MAX_FILE_SIZE = 10 * 1024 * 1024


def _determine_extension(content_type: str, filename: str | None) -> str:
    if filename and "." in filename:
        ext = filename.rsplit(".", 1)[-1].lower()
        if ext in ('jpg', 'jpeg', 'png', 'gif', 'webp'):
            return ext

    mime_to_ext = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/gif": "gif",
        "image/webp": "webp",
    }
    return mime_to_ext.get(content_type, "jpg")


def _upload_to_oss(file_data: bytes, upload_date: str, stored_filename: str, content_type: str) -> str | None:
    """
    尝试上传文件到OSS

    Returns:
        str: OSS URL，上传失败返回None
    """
    try:
        oss: OSSService = get_oss_service()
        if not oss.is_available:
            return None

        oss_key = OSSService.generate_oss_key(upload_date, stored_filename)
        url = oss.upload_file(file_data, oss_key, content_type)
        return url
    except Exception as e:
        logger.warning(f"OSS上传失败，降级到数据库存储: {str(e)}")
        return None


@router.post("", response_model=ApiResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_user_required)
):
    """
    上传文件

    优先存储到阿里云OSS，OSS不可用时降级到数据库存储
    """
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请选择要上传的文件"
        )

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持上传图片文件（JPEG、PNG、GIF、WebP）"
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件大小不能超过10MB"
        )
    
    try:
        compressed_content, compressed_content_type = compress_image(
            content,
            quality=85,
            max_size=(1920, 1920),
            convert_to_jpeg=True
        )
        
        if len(compressed_content) < len(content):
            content = compressed_content
            file.content_type = compressed_content_type
            logger.info(f"图片压缩成功: {len(compressed_content)} bytes (原始: {len(content)} bytes)")
    except Exception as e:
        logger.warning(f"图片压缩失败,使用原始图片: {str(e)}")

    today = datetime.now().strftime("%Y%m%d")
    file_ext = _determine_extension(file.content_type, file.filename)
    file_id = str(uuid.uuid4())
    stored_filename = f"{uuid.uuid4().hex}.{file_ext}"
    file_path = UploadedFile.generate_file_path(today, stored_filename)

    oss_url = _upload_to_oss(content, today, stored_filename, file.content_type)

    if oss_url:
        uploaded_file = UploadedFile(
            file_id=file_id,
            original_filename=file.filename,
            stored_filename=stored_filename,
            content_type=file.content_type,
            file_data=None,
            file_size=len(content),
            file_path=file_path,
            upload_date=today,
            storage_type="oss",
            oss_url=oss_url,
        )
    else:
        uploaded_file = UploadedFile(
            file_id=file_id,
            original_filename=file.filename,
            stored_filename=stored_filename,
            content_type=file.content_type,
            file_data=content,
            file_size=len(content),
            file_path=file_path,
            upload_date=today,
            storage_type="database",
            oss_url=None,
        )

    db.add(uploaded_file)
    db.commit()
    db.refresh(uploaded_file)

    return ApiResponse(
        code=200,
        message="上传成功",
        data={
            "url": file_path,
            "file_id": file_id,
            "filename": stored_filename
        }
    )


@router.post("/base64", response_model=ApiResponse)
async def upload_base64(
    data: dict,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_user_required)
):
    """
    上传Base64编码的图片

    优先存储到阿里云OSS，OSS不可用时降级到数据库存储
    """
    import imghdr

    base64_str = data.get("data")
    filename = data.get("filename")

    if not base64_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请提供base64编码的图片数据"
        )

    if base64_str.startswith("data:image"):
        base64_str = base64_str.split(",")[1]

    try:
        image_data = base64.b64decode(base64_str)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的base64图片数据"
        ) from None

    if len(image_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件大小不能超过10MB"
        )
    
    try:
        compressed_data, compressed_content_type = compress_image(
            image_data,
            quality=85,
            max_size=(1920, 1920),
            convert_to_jpeg=True
        )
        
        if len(compressed_data) < len(image_data):
            image_data = compressed_data
            content_type = compressed_content_type
            logger.info(f"Base64图片压缩成功: {len(compressed_data)} bytes (原始: {len(image_data)} bytes)")
    except Exception as e:
        logger.warning(f"Base64图片压缩失败,使用原始图片: {str(e)}")

    image_type = imghdr.what(None, h=image_data)
    if image_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的图片类型，只支持JPEG、PNG、GIF、WebP格式，检测到: {image_type or '未知'}"
        )

    file_ext = IMAGE_TYPE_TO_EXT.get(image_type, 'png')
    content_type = IMAGE_TYPE_TO_MIME.get(image_type, 'image/png')

    today = datetime.now().strftime("%Y%m%d")
    file_id = str(uuid.uuid4())
    stored_filename = f"{uuid.uuid4().hex}.{file_ext}"
    file_path = UploadedFile.generate_file_path(today, stored_filename)

    oss_url = _upload_to_oss(image_data, today, stored_filename, content_type)

    if oss_url:
        uploaded_file = UploadedFile(
            file_id=file_id,
            original_filename=filename or f"image.{file_ext}",
            stored_filename=stored_filename,
            content_type=content_type,
            file_data=None,
            file_size=len(image_data),
            file_path=file_path,
            upload_date=today,
            storage_type="oss",
            oss_url=oss_url,
        )
    else:
        uploaded_file = UploadedFile(
            file_id=file_id,
            original_filename=filename or f"image.{file_ext}",
            stored_filename=stored_filename,
            content_type=content_type,
            file_data=image_data,
            file_size=len(image_data),
            file_path=file_path,
            upload_date=today,
            storage_type="database",
            oss_url=None,
        )

    db.add(uploaded_file)
    db.commit()
    db.refresh(uploaded_file)

    return ApiResponse(
        code=200,
        message="上传成功",
        data={
            "url": file_path,
            "file_id": file_id,
            "filename": stored_filename
        }
    )
