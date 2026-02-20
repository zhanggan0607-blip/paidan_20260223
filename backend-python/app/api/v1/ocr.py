# -*- coding: utf-8 -*-
"""
OCR识别API接口
提供身份证识别功能
使用阿里云OCR引擎
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import logging

from app.schemas.common import ApiResponse
from app.utils.aliyun_ocr import get_ocr_service
from app.utils.id_card_validator import validate_id_card

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ocr", tags=["OCR Recognition"])


class IdCardRecognizeRequest(BaseModel):
    """身份证识别请求"""
    imageUrl: Optional[str] = None
    imageBase64: Optional[str] = None
    side: str = 'face'


class IdCardFrontResult(BaseModel):
    """身份证正面识别结果"""
    name: str = ''
    gender: str = ''
    nationality: str = ''
    birthDate: str = ''
    address: str = ''
    idCardNumber: str = ''


class IdCardBackResult(BaseModel):
    """身份证反面识别结果"""
    issuingAuthority: str = ''
    validPeriod: str = ''


@router.post("/idcard", response_model=ApiResponse)
def recognize_idcard(request: IdCardRecognizeRequest):
    """
    身份证OCR识别
    
    使用阿里云OCR引擎识别身份证正反面
    
    Args:
        request: 识别请求，包含图片URL或Base64编码，以及身份证面（face/back）
        
    Returns:
        ApiResponse: 识别结果
    """
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
    
    try:
        if request.imageUrl:
            result = ocr_service.recognize_idcard(request.imageUrl, request.side)
        else:
            result = ocr_service.recognize_idcard_base64(request.imageBase64, request.side)
        
        logger.info(f"OCR识别结果: {result}")
        
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
        logger.error(f"身份证识别异常: {str(e)}", exc_info=True)
        return ApiResponse(
            code=500,
            message=f"识别异常: {str(e)}",
            data=None
        )


@router.get("/status", response_model=ApiResponse)
def get_ocr_status():
    """
    获取OCR服务状态
    
    Returns:
        ApiResponse: 服务状态信息
    """
    ocr_service = get_ocr_service()
    
    return ApiResponse(
        code=200,
        message="success",
        data={
            "configured": ocr_service.is_configured(),
            "service": "Aliyun OCR"
        }
    )
