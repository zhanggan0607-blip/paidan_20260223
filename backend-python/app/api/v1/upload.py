"""
文件上传API
将图片等文件存储在数据库中，确保数据永久保存在阿里云RDS
"""
import base64
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.uploaded_file import UploadedFile
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/upload", tags=["File Upload"])


@router.post("", response_model=ApiResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    上传文件到数据库
    
    将文件以二进制形式存储在数据库中，确保数据永久保存
    """
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请选择要上传的文件"
        )

    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持上传图片文件（JPEG、PNG、GIF、WebP）"
        )

    max_size = 10 * 1024 * 1024
    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件大小不能超过10MB"
        )

    today = datetime.now().strftime("%Y%m%d")
    file_ext = ""
    if file.filename:
        file_ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else ""
    
    if not file_ext:
        if file.content_type == "image/jpeg":
            file_ext = "jpg"
        elif file.content_type == "image/png":
            file_ext = "png"
        elif file.content_type == "image/gif":
            file_ext = "gif"
        elif file.content_type == "image/webp":
            file_ext = "webp"
        else:
            file_ext = "jpg"

    file_id = str(uuid.uuid4())
    stored_filename = f"{uuid.uuid4().hex}.{file_ext}"
    file_path = UploadedFile.generate_file_path(today, stored_filename)

    uploaded_file = UploadedFile(
        file_id=file_id,
        original_filename=file.filename,
        stored_filename=stored_filename,
        content_type=file.content_type,
        file_data=content,
        file_size=len(content),
        file_path=file_path,
        upload_date=today
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
    db: Session = Depends(get_db)
):
    """
    上传Base64编码的图片到数据库
    
    将Base64图片解码后以二进制形式存储在数据库中
    """
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

    max_size = 10 * 1024 * 1024
    if len(image_data) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件大小不能超过10MB"
        )

    today = datetime.now().strftime("%Y%m%d")
    file_id = str(uuid.uuid4())
    stored_filename = f"{uuid.uuid4().hex}.png"
    file_path = UploadedFile.generate_file_path(today, stored_filename)

    uploaded_file = UploadedFile(
        file_id=file_id,
        original_filename=filename or "image.png",
        stored_filename=stored_filename,
        content_type="image/png",
        file_data=image_data,
        file_size=len(image_data),
        file_path=file_path,
        upload_date=today
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
