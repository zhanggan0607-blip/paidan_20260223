"""
文件服务API
从数据库读取上传的文件，确保数据永久保存在阿里云RDS
支持OSS自愈：当数据库记录缺失时，自动从OSS恢复
"""
import os
import uuid
from io import BytesIO
from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import StreamingResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.uploaded_file import UploadedFile
from app.utils.logging_config import get_logger
from app.utils import get_inline_content_disposition
from app.utils.oss_service import get_oss_service, OSSService
from app.dependencies import get_current_user_required, get_current_user_info, UserInfo

logger = get_logger(__name__)

router = APIRouter(prefix="/files", tags=["File Service"])

UPLOAD_DIR = "/app/uploads"

THUMBNAIL_CACHE = {}
THUMBNAIL_MAX_CACHE_SIZE = 100


def _parse_token_from_query(token: str) -> UserInfo | None:
    from app.dependencies import _parse_jwt_token
    user_data = _parse_jwt_token(token)
    if not user_data:
        return None
    return UserInfo(
        id=user_data.get('user_id') or user_data.get('id'),
        name=user_data.get('sub') or user_data.get('name'),
        role=user_data.get('role', '运维人员'),
        token=token
    )


def _try_recover_from_oss(file_path: str, upload_date: str, filename: str, db: Session) -> UploadedFile | None:
    """
    自愈机制：当数据库记录缺失时，尝试从OSS恢复

    如果文件存在于OSS，自动创建uploaded_file记录并返回

    Args:
        file_path: 文件路径 /uploads/YYYYMMDD/xxx.jpg
        upload_date: 上传日期
        filename: 文件名
        db: 数据库会话

    Returns:
        UploadedFile | None: 恢复的记录，或None
    """
    try:
        oss: OSSService = get_oss_service()
        if not oss.is_available:
            return None

        oss_key = OSSService.generate_oss_key(upload_date, filename)

        if not oss.file_exists(oss_key):
            logger.info(f"OSS自愈检查: 文件不存在于OSS, oss_key={oss_key}")
            return None

        oss_url = oss.get_file_url(oss_key)
        logger.info(f"OSS自愈: 在OSS中发现文件, 正在恢复数据库记录, file_path={file_path}, oss_url={oss_url}")

        content_type = "image/jpeg"
        if filename.lower().endswith(".png"):
            content_type = "image/png"
        elif filename.lower().endswith(".gif"):
            content_type = "image/gif"
        elif filename.lower().endswith(".webp"):
            content_type = "image/webp"

        recovered_file = UploadedFile(
            file_id=str(uuid.uuid4()),
            original_filename=filename,
            stored_filename=filename,
            content_type=content_type,
            file_data=None,
            file_size=0,
            file_path=file_path,
            upload_date=upload_date,
            storage_type="oss",
            oss_url=oss_url,
        )

        db.add(recovered_file)
        db.commit()
        db.refresh(recovered_file)

        logger.info(f"OSS自愈: 数据库记录已恢复, file_id={recovered_file.file_id}")
        return recovered_file
    except Exception as e:
        logger.error(f"OSS自愈失败: file_path={file_path}, error={e}")
        try:
            db.rollback()
        except Exception:
            pass
        return None


def _get_content_type(filename: str) -> str:
    if filename.lower().endswith(".png"):
        return "image/png"
    elif filename.lower().endswith(".gif"):
        return "image/gif"
    elif filename.lower().endswith(".webp"):
        return "image/webp"
    return "image/jpeg"


def _generate_placeholder_image(filename: str) -> StreamingResponse:
    try:
        from PIL import Image, ImageDraw, ImageFont

        img = Image.new('RGB', (300, 200), color=(245, 245, 245))
        draw = ImageDraw.Draw(img)

        draw.rectangle([10, 10, 290, 190], outline=(220, 220, 220), width=2)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except Exception:
            font = ImageFont.load_default()

        draw.text((80, 70), "图片未找到", fill=(180, 180, 180), font=font)
        draw.text((70, 100), "Image Not Found", fill=(200, 200, 200), font=font)

        output = BytesIO()
        img.save(output, format='PNG')
        placeholder_data = output.getvalue()
    except Exception as placeholder_err:
        logger.error(f"生成占位图片失败: {placeholder_err}")
        png_1x1 = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
        placeholder_data = png_1x1

    return StreamingResponse(
        BytesIO(placeholder_data),
        media_type="image/png",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "Content-Disposition": get_inline_content_disposition(f"placeholder_{filename}")
        }
    )


@router.get("/{upload_date}/{filename}")
async def get_file(
    upload_date: str,
    filename: str,
    request: Request,
    token: str | None = Query(None, description="Access token for img tag authentication"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    if not user_info.is_authenticated and token:
        user_data = _parse_token_from_query(token)
        if user_data:
            user_info = user_data

    if not user_info.is_authenticated:
        from fastapi import HTTPException, status as http_status
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="未登录或登录已过期"
        )
    file_path = f"/uploads/{upload_date}/{filename}"

    logger.info(f"文件访问: {file_path}, user={user_info.name}, ip={request.client.host if request.client else 'unknown'}")

    uploaded_file = db.query(UploadedFile).filter(
        UploadedFile.file_path == file_path
    ).first()

    if uploaded_file:
        if uploaded_file.storage_type == "oss" and uploaded_file.oss_url:
            logger.info(f"重定向到OSS: {file_path}")
            return RedirectResponse(url=uploaded_file.oss_url)

        if uploaded_file.file_data:
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
        else:
            logger.warning(f"数据库记录存在但file_data为空且无oss_url: {file_path}, 尝试OSS自愈")
            recovered = _try_recover_from_oss(file_path, upload_date, filename, db)
            if recovered:
                return RedirectResponse(url=recovered.oss_url)

    file_system_path = os.path.join(UPLOAD_DIR, upload_date, filename)
    if os.path.exists(file_system_path):
        logger.info(f"从文件系统读取文件(兼容旧数据): {file_path}")
        content_type = _get_content_type(filename)

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

    logger.warning(f"文件不在数据库和文件系统中, 尝试OSS自愈: {file_path}")
    recovered = _try_recover_from_oss(file_path, upload_date, filename, db)
    if recovered:
        logger.info(f"OSS自愈成功, 重定向到OSS: {file_path}")
        return RedirectResponse(url=recovered.oss_url)

    logger.warning(f"文件不存在(数据库/文件系统/OSS均未找到): {file_path}, 返回占位图片")
    return _generate_placeholder_image(filename)


@router.get("/by-id/{file_id}")
async def get_file_by_id(
    file_id: str,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    uploaded_file = db.query(UploadedFile).filter(
        UploadedFile.file_id == file_id
    ).first()

    if not uploaded_file:
        logger.warning(f"文件不存在: file_id={file_id}")
        raise HTTPException(status_code=404, detail="文件不存在")

    if uploaded_file.storage_type == "oss" and uploaded_file.oss_url:
        logger.info(f"通过ID重定向到OSS: file_id={file_id}")
        return RedirectResponse(url=uploaded_file.oss_url)

    if not uploaded_file.file_data:
        logger.warning(f"文件数据为空: file_id={file_id}, file_path={uploaded_file.file_path}")
        if uploaded_file.file_path:
            parts = uploaded_file.file_path.strip("/").split("/")
            if len(parts) >= 3:
                upload_date = parts[1]
                filename = parts[2]
                recovered = _try_recover_from_oss(uploaded_file.file_path, upload_date, filename, db)
                if recovered:
                    return RedirectResponse(url=recovered.oss_url)
        raise HTTPException(status_code=404, detail="文件数据不存在")

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


def generate_thumbnail(image_data: bytes, size: int = 200) -> bytes:
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


@router.get("/thumbnail/{upload_date}/{filename}")
async def get_thumbnail(
    upload_date: str,
    filename: str,
    size: int = Query(200, ge=50, le=500, description="缩略图尺寸"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
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

    image_data = None

    if uploaded_file:
        if uploaded_file.storage_type == "oss" and uploaded_file.oss_url:
            try:
                import urllib.request
                with urllib.request.urlopen(uploaded_file.oss_url, timeout=30) as resp:
                    image_data = resp.read()
            except Exception as e:
                logger.error(f"从OSS下载文件失败: {e}")
                raise HTTPException(status_code=502, detail="从OSS获取文件失败")
        elif uploaded_file.file_data:
            image_data = uploaded_file.file_data
        else:
            recovered = _try_recover_from_oss(file_path, upload_date, filename, db)
            if recovered and recovered.oss_url:
                try:
                    import urllib.request
                    with urllib.request.urlopen(recovered.oss_url, timeout=30) as resp:
                        image_data = resp.read()
                except Exception as e:
                    logger.error(f"自愈后从OSS下载文件失败: {e}")
                    raise HTTPException(status_code=502, detail="从OSS获取文件失败")
    else:
        file_system_path = os.path.join(UPLOAD_DIR, upload_date, filename)
        if os.path.exists(file_system_path):
            with open(file_system_path, "rb") as f:
                image_data = f.read()
        else:
            recovered = _try_recover_from_oss(file_path, upload_date, filename, db)
            if recovered and recovered.oss_url:
                try:
                    import urllib.request
                    with urllib.request.urlopen(recovered.oss_url, timeout=30) as resp:
                        image_data = resp.read()
                except Exception as e:
                    logger.error(f"自愈后从OSS下载文件失败: {e}")
                    raise HTTPException(status_code=502, detail="从OSS获取文件失败")

    if image_data is None:
        raise HTTPException(status_code=404, detail="文件不存在")

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


@router.get("/diagnose/check-file")
async def check_file_status(
    file_path: str = Query(..., description="文件路径，如 /uploads/20260327/xxx.jpg"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):

    result = {
        "file_path": file_path,
        "in_database": False,
        "in_filesystem": False,
        "in_oss": False,
        "database_record": None,
        "oss_url": None,
    }

    uploaded_file = db.query(UploadedFile).filter(
        UploadedFile.file_path == file_path
    ).first()

    if uploaded_file:
        result["in_database"] = True
        result["database_record"] = {
            "file_id": uploaded_file.file_id,
            "storage_type": uploaded_file.storage_type,
            "oss_url": uploaded_file.oss_url,
            "content_type": uploaded_file.content_type,
            "file_size": uploaded_file.file_size,
            "has_file_data": uploaded_file.file_data is not None and len(uploaded_file.file_data) > 0,
            "upload_date": uploaded_file.upload_date,
            "created_at": str(uploaded_file.created_at) if uploaded_file.created_at else None,
        }
        if uploaded_file.oss_url:
            result["oss_url"] = uploaded_file.oss_url

    parts = file_path.strip("/").split("/")
    if len(parts) >= 3:
        upload_date = parts[1]
        filename = parts[2]

        file_system_path = os.path.join(UPLOAD_DIR, upload_date, filename)
        result["in_filesystem"] = os.path.exists(file_system_path)

        try:
            oss: OSSService = get_oss_service()
            if oss.is_available:
                oss_key = OSSService.generate_oss_key(upload_date, filename)
                result["in_oss"] = oss.file_exists(oss_key)
                if result["in_oss"]:
                    result["oss_url"] = oss.get_file_url(oss_key)
        except Exception as e:
            result["oss_error"] = str(e)

    return result


@router.get("/diagnose/orphaned-references")
async def find_orphaned_references(
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    if not user_info.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")

    from app.models.spot_work_worker import SpotWorkWorker

    workers = db.query(SpotWorkWorker).filter(
        (SpotWorkWorker.id_card_front.isnot(None)) | (SpotWorkWorker.id_card_back.isnot(None))
    ).all()

    orphaned = []
    for worker in workers:
        for field, value in [("id_card_front", worker.id_card_front), ("id_card_back", worker.id_card_back)]:
            if not value or not value.startswith("/uploads/"):
                continue

            exists_in_db = db.query(UploadedFile).filter(
                UploadedFile.file_path == value
            ).first()

            if not exists_in_db:
                orphaned.append({
                    "worker_id": worker.id,
                    "worker_name": worker.name,
                    "field": field,
                    "file_path": value,
                })

    return {
        "total_workers_with_photos": len(workers),
        "orphaned_count": len(orphaned),
        "orphaned_references": orphaned,
    }
