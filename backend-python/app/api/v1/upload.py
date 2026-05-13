"""
文件上传API
优先将图片等文件存储到阿里云OSS，OSS不可用时降级到数据库存储
"""
import base64
import os
import uuid
from datetime import datetime
from uuid import uuid4

import filetype
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from typing import List
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

ALLOWED_IMAGE_TYPES = {'jpeg', 'png', 'gif', 'webp', 'heic', 'heif', 'avif'}
IMAGE_TYPE_TO_EXT = {
    'jpeg': 'jpg',
    'png': 'png',
    'gif': 'gif',
    'webp': 'webp',
    'heic': 'jpg',
    'heif': 'jpg',
    'avif': 'jpg',
}
IMAGE_TYPE_TO_MIME = {
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'webp': 'image/webp',
    'heic': 'image/heic',
    'heif': 'image/heif',
    'avif': 'image/avif',
}
ALLOWED_CONTENT_TYPES = [
    "image/jpeg", "image/png", "image/gif", "image/webp",
    "image/heic", "image/heif", "image/avif",
]
MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_BATCH_COUNT = 9


def _sanitize_filename(filename: str | None) -> str:
    if not filename:
        return "unknown"
    safe_name = os.path.basename(filename)
    safe_name = safe_name.replace("..", "").replace("/", "").replace("\\", "")
    return safe_name if safe_name else "unknown"


def _validate_image_content(content: bytes) -> str:
    kind = filetype.guess(content)
    if kind is None:
        if _is_heic_heif(content):
            return 'image/heic'
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法识别文件类型，请上传有效的图片文件"
        )

    detected_mime = kind.mime
    if detected_mime not in ALLOWED_CONTENT_TYPES:
        if detected_mime in ('image/heic', 'image/heif', 'image/avif'):
            return detected_mime
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持上传图片文件（JPEG、PNG、GIF、WebP、HEIC）"
        )

    return detected_mime


def _is_heic_heif(content: bytes) -> bool:
    if len(content) < 12:
        return False
    box_type = content[4:8]
    if box_type == b'ftyp':
        brand = content[8:12]
        return brand in (b'heic', b'heix', b'hevc', b'hevx', b'heim', b'heis', b'hevm', b'hevs', b'mif1')
    return False


def _determine_extension(content_type: str, filename: str | None) -> str:
    if filename and "." in filename:
        ext = filename.rsplit(".", 1)[-1].lower()
        if ext in ('jpg', 'jpeg', 'png', 'gif', 'webp', 'heic', 'heif', 'avif'):
            if ext in ('heic', 'heif', 'avif'):
                return 'jpg'
            return ext

    mime_to_ext = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/gif": "gif",
        "image/webp": "webp",
        "image/heic": "jpg",
        "image/heif": "jpg",
        "image/avif": "jpg",
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

    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只支持上传图片文件（JPEG、PNG、GIF、WebP、HEIC）"
            )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件大小不能超过10MB"
        )

    _validate_image_content(content)

    try:
        compressed_content, compressed_content_type = compress_image(
            content,
            quality=75,
            max_size=(1280, 1280),
            convert_to_jpeg=True
        )

        original_size = len(content)
        if len(compressed_content) < original_size:
            content = compressed_content
            file.content_type = compressed_content_type
            logger.info(f"图片压缩成功: {len(compressed_content)} bytes (原始: {original_size} bytes)")
    except ValueError as e:
        logger.warning(f"图片压缩失败，使用原始图片: {str(e)}")
    except Exception as e:
        logger.warning(f"图片处理异常，使用原始图片: {type(e).__name__}: {str(e)}")

    today = datetime.now().strftime("%Y%m%d")
    file_ext = _determine_extension(file.content_type, file.filename)
    file_id = str(uuid.uuid4())
    stored_filename = f"{uuid.uuid4().hex}.{file_ext}"
    file_path = UploadedFile.generate_file_path(today, stored_filename)

    oss_url = _upload_to_oss(content, today, stored_filename, file.content_type)
    storage_type = "oss" if oss_url else "database"
    file_data = None if oss_url else content

    uploaded_file = UploadedFile(
        file_id=file_id,
        original_filename=_sanitize_filename(file.filename),
        stored_filename=stored_filename,
        content_type=file.content_type,
        file_data=file_data,
        file_size=len(content),
        file_path=file_path,
        upload_date=today,
        storage_type=storage_type,
        oss_url=oss_url,
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


async def _process_single_upload(file: UploadFile, db: Session) -> dict:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件 {file.filename} 类型不支持，只支持JPEG、PNG、GIF、WebP格式"
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件 {file.filename} 大小不能超过10MB"
        )

    _validate_image_content(content)

    try:
        compressed_content, compressed_content_type = compress_image(
            content,
            quality=75,
            max_size=(1280, 1280),
            convert_to_jpeg=True
        )
        original_size = len(content)
        if len(compressed_content) < original_size:
            content = compressed_content
            file.content_type = compressed_content_type
    except Exception as e:
        logger.warning(f"文件 {file.filename} 压缩失败，使用原始图片: {str(e)}")

    today = datetime.now().strftime("%Y%m%d")
    file_ext = _determine_extension(file.content_type, file.filename)
    file_id = str(uuid.uuid4())
    stored_filename = f"{uuid.uuid4().hex}.{file_ext}"
    file_path = UploadedFile.generate_file_path(today, stored_filename)

    oss_url = _upload_to_oss(content, today, stored_filename, file.content_type)
    storage_type = "oss" if oss_url else "database"
    file_data = None if oss_url else content

    uploaded_file = UploadedFile(
        file_id=file_id,
        original_filename=_sanitize_filename(file.filename),
        stored_filename=stored_filename,
        content_type=file.content_type,
        file_data=file_data,
        file_size=len(content),
        file_path=file_path,
        upload_date=today,
        storage_type=storage_type,
        oss_url=oss_url,
    )

    db.add(uploaded_file)
    db.commit()
    db.refresh(uploaded_file)

    return {
        "url": file_path,
        "file_id": file_id,
        "filename": stored_filename
    }


@router.post("/batch", response_model=ApiResponse)
async def upload_batch(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_user_required)
):
    if len(files) > MAX_BATCH_COUNT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"最多同时上传{MAX_BATCH_COUNT}张图片"
        )

    if len(files) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请选择要上传的文件"
        )

    results = []
    failed = []
    for i, file in enumerate(files):
        try:
            result = await _process_single_upload(file, db)
            results.append(result)
        except HTTPException as e:
            failed.append({"index": i, "filename": file.filename, "error": e.detail})
        except Exception as e:
            logger.error(f"批量上传第{i+1}个文件失败: {str(e)}")
            failed.append({"index": i, "filename": file.filename, "error": str(e)})

    return ApiResponse(
        code=200,
        message=f"成功上传{len(results)}张图片" + (f"，{len(failed)}张失败" if failed else ""),
        data={
            "success": results,
            "failed": failed,
        }
    )


@router.post("/base64", response_model=ApiResponse)
async def upload_base64(
    data: dict,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_user_required)
):
    base64_str = data.get("data")
    filename = data.get("filename")

    if not base64_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请提供base64编码的图片数据"
        )

    if base64_str.startswith("data:image"):
        parts = base64_str.split(",", 1)
        if len(parts) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的data URI格式"
            )
        base64_str = parts[1]

    max_base64_length = MAX_FILE_SIZE * 2
    if len(base64_str) > max_base64_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件大小不能超过10MB"
        )

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

    _validate_image_content(image_data)

    try:
        compressed_data, compressed_content_type = compress_image(
            image_data,
            quality=75,
            max_size=(1280, 1280),
            convert_to_jpeg=True
        )

        original_size = len(image_data)
        if len(compressed_data) < original_size:
            image_data = compressed_data
            content_type = compressed_content_type
            logger.info(f"Base64图片压缩成功: {len(compressed_data)} bytes (原始: {original_size} bytes)")
        else:
            detected_mime = _validate_image_content(image_data)
            content_type = detected_mime
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Base64图片压缩失败，使用原始图片: {str(e)}")
        content_type = 'image/jpeg'

    today = datetime.now().strftime("%Y%m%d")
    file_id = str(uuid.uuid4())
    file_ext = _determine_extension(content_type, filename)
    stored_filename = f"{uuid.uuid4().hex}.{file_ext}"
    file_path = UploadedFile.generate_file_path(today, stored_filename)

    oss_url = _upload_to_oss(image_data, today, stored_filename, content_type)
    storage_type = "oss" if oss_url else "database"
    file_data = None if oss_url else image_data

    uploaded_file = UploadedFile(
        file_id=file_id,
        original_filename=filename or f"image.{file_ext}",
        stored_filename=stored_filename,
        content_type=content_type,
        file_data=file_data,
        file_size=len(image_data),
        file_path=file_path,
        upload_date=today,
        storage_type=storage_type,
        oss_url=oss_url,
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
