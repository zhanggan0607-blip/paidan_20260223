import os
import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.schemas.common import ApiResponse
from app.config import get_settings

router = APIRouter(prefix="/upload", tags=["File Upload"])
settings = get_settings()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("", response_model=ApiResponse)
async def upload_file(file: UploadFile = File(...)):
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
    upload_path = os.path.join(UPLOAD_DIR, today)
    os.makedirs(upload_path, exist_ok=True)
    
    file_ext = os.path.splitext(file.filename or "image.jpg")[1]
    if not file_ext:
        file_ext = ".jpg"
    
    new_filename = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(upload_path, new_filename)
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    file_url = f"/uploads/{today}/{new_filename}"
    
    return ApiResponse(
        code=200,
        message="上传成功",
        data={"url": file_url, "filename": new_filename}
    )


@router.post("/base64", response_model=ApiResponse)
async def upload_base64(data: dict):
    import base64
    
    base64_str = data.get("data")
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
        )
    
    today = datetime.now().strftime("%Y%m%d")
    upload_path = os.path.join(UPLOAD_DIR, today)
    os.makedirs(upload_path, exist_ok=True)
    
    new_filename = f"{uuid.uuid4().hex}.png"
    file_path = os.path.join(upload_path, new_filename)
    
    with open(file_path, "wb") as f:
        f.write(image_data)
    
    file_url = f"/uploads/{today}/{new_filename}"
    
    return ApiResponse(
        code=200,
        message="上传成功",
        data={"url": file_url, "filename": new_filename}
    )
