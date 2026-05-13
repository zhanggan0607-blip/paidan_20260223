"""
OCR识别API接口
提供身份证识别功能
使用阿里云OCR引擎
"""

import time
import uuid

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

from app.dependencies import UserInfo, get_current_user_required
from app.schemas.common import ApiResponse
from app.utils.aliyun_ocr import get_ocr_service
from app.utils.id_card_validator import validate_id_card
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/ocr", tags=["OCR Recognition"])


class IdCardRecognizeRequest(BaseModel):
    imageUrl: str | None = None
    imageBase64: str | None = None
    side: str = 'face'


def _compress_ocr_image(image_bytes: bytes, max_size: int = 1280) -> bytes:
    try:
        from app.utils.image_compression import compress_image
        compressed, _ = compress_image(
            image_bytes,
            quality=80,
            max_size=(max_size, max_size),
            convert_to_jpeg=True
        )
        if len(compressed) < len(image_bytes):
            logger.info(f"OCR图片压缩: {len(image_bytes)} -> {len(compressed)} bytes")
            return compressed
    except Exception as e:
        logger.warning(f"OCR图片压缩失败，使用原始图片: {e}")
    return image_bytes


@router.post("/idcard", response_model=ApiResponse)
def recognize_idcard(
    request: IdCardRecognizeRequest,
    user_info: UserInfo = Depends(get_current_user_required)
):
    ocr_service = get_ocr_service()

    if not ocr_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OCR服务未配置，请联系管理员配置阿里云AccessKey"
        )

    if not request.imageUrl and not request.imageBase64:
        return ApiResponse(
            code=400,
            message="请提供图片URL或Base64编码",
            data=None
        )

    if request.side not in ('face', 'back'):
        return ApiResponse(
            code=400,
            message="side参数必须为face或back",
            data=None
        )

    try:
        total_start = time.time()

        if request.imageUrl:
            result = ocr_service.recognize_idcard(request.imageUrl, request.side)
        else:
            import base64
            image_bytes = base64.b64decode(request.imageBase64)
            image_size_kb = len(image_bytes) / 1024
            logger.info(f"OCR请求: side={request.side}, 图片大小={image_size_kb:.1f}KB")

            if image_size_kb > 512:
                compress_start = time.time()
                image_bytes = _compress_ocr_image(image_bytes)
                compress_time = time.time() - compress_start
                logger.info(f"OCR图片压缩耗时: {compress_time:.2f}s, 压缩后={len(image_bytes) / 1024:.1f}KB")
                compressed_base64 = base64.b64encode(image_bytes).decode('utf-8')
                result = ocr_service.recognize_idcard_base64(compressed_base64, request.side)
            else:
                logger.info(f"图片已由前端压缩({image_size_kb:.1f}KB)，跳过后端压缩")
                result = ocr_service.recognize_idcard_base64(request.imageBase64, request.side)

        ocr_time = time.time() - total_start
        logger.info(f"OCR识别结果: side={request.side}, success={result['success']}, 总耗时={ocr_time:.2f}s")

        if result['success']:
            data = result.get('data', {})

            if request.side == 'face' and data.get('idCardNumber'):
                is_valid, msg, birth_date, gender = validate_id_card(data['idCardNumber'])
                if not is_valid:
                    logger.warning(f"OCR识别的身份证号码验证失败: {msg}")
                    data['validationWarning'] = msg
                else:
                    if birth_date and not data.get('birthDate'):
                        data['birthDate'] = birth_date
                    if gender and not data.get('gender'):
                        data['gender'] = gender

            logger.info(f"身份证识别成功: side={request.side}")
            return ApiResponse(
                code=200,
                message="识别成功",
                data=data
            )
        else:
            logger.warning(f"身份证识别失败: {result['message']}")
            return ApiResponse(
                code=400,
                message=result['message'],
                data=None
            )

    except Exception as e:
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 身份证识别异常: {str(e)}", exc_info=True)
        return ApiResponse(
            code=500,
            message=f"识别异常，错误ID: {error_id}，请联系管理员",
            data=None
        )


@router.get("/status", response_model=ApiResponse)
def get_ocr_status(
    user_info: UserInfo = Depends(get_current_user_required)
):
    ocr_service = get_ocr_service()

    return ApiResponse(
        code=200,
        message="success",
        data={
            "configured": ocr_service.is_configured(),
            "service": "Aliyun OCR"
        }
    )
