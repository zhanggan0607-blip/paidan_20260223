# -*- coding: utf-8 -*-
"""
阿里云OCR身份证识别服务
支持身份证正反面识别
使用新版SDK支持Base64编码图片
"""

import base64
import io
import logging
from typing import Optional, Dict, Any

from alibabacloud_ocr20191230.client import Client
from alibabacloud_ocr20191230.models import RecognizeIdentityCardAdvanceRequest
from alibabacloud_tea_openapi.models import Config
from alibabacloud_tea_util.models import RuntimeOptions

from app.config import get_settings

logger = logging.getLogger(__name__)


class AliyunOCRService:
    """
    阿里云OCR身份证识别服务类
    
    使用阿里云OCR API识别身份证正反面信息
    """
    
    _instance: Optional['AliyunOCRService'] = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        """
        单例模式，确保只有一个客户端实例
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        初始化阿里云OCR客户端
        """
        if self._client is None:
            settings = get_settings()
            access_key_id = settings.aliyun_access_key_id
            access_key_secret = settings.aliyun_access_key_secret
            region_id = settings.aliyun_ocr_region_id
            
            if not access_key_id or not access_key_secret:
                logger.warning("阿里云OCR配置未设置，请检查ALIYUN_ACCESS_KEY_ID和ALIYUN_ACCESS_KEY_SECRET")
                self._client = None
            else:
                try:
                    config = Config(
                        access_key_id=access_key_id,
                        access_key_secret=access_key_secret,
                        endpoint='ocr.cn-shanghai.aliyuncs.com',
                        region_id=region_id
                    )
                    self._client = Client(config)
                    logger.info(f"阿里云OCR客户端初始化成功，区域: {region_id}")
                except Exception as e:
                    logger.error(f"阿里云OCR客户端初始化失败: {str(e)}")
                    self._client = None
    
    def is_configured(self) -> bool:
        """
        检查OCR服务是否已配置
        
        Returns:
            bool: 是否已配置
        """
        return self._client is not None
    
    def recognize_idcard_base64(self, image_base64: str, side: str = 'face') -> Dict[str, Any]:
        """
        通过Base64编码识别身份证信息
        
        Args:
            image_base64: 图片Base64编码（不含data:image前缀）
            side: 身份证面，'face'为正面，'back'为反面
            
        Returns:
            Dict[str, Any]: 识别结果
        """
        if not self._client:
            return {
                'success': False,
                'message': '阿里云OCR服务未配置，请检查AccessKey配置'
            }
        
        try:
            image_bytes = base64.b64decode(image_base64)
            image_stream = io.BytesIO(image_bytes)
            
            request = RecognizeIdentityCardAdvanceRequest(
                image_urlobject=image_stream,
                side=side
            )
            
            runtime = RuntimeOptions()
            response = self._client.recognize_identity_card_advance(request, runtime)
            
            if response.body and response.body.data:
                data = response.body.data
                parsed = self._parse_idcard_result(data, side)
                logger.info(f"OCR识别成功: side={side}, result={parsed}")
                return {
                    'success': True,
                    'message': '识别成功',
                    'data': parsed
                }
            else:
                logger.error(f"OCR识别失败: 无返回数据")
                return {
                    'success': False,
                    'message': 'OCR识别失败，请检查图片是否清晰'
                }
                
        except Exception as e:
            error_msg = str(e)
            if hasattr(e, 'code'):
                error_msg = f"{e.code}: {error_msg}"
            logger.error(f"OCR识别异常: {error_msg}", exc_info=True)
            return {
                'success': False,
                'message': f'识别异常: {error_msg}'
            }
    
    def recognize_idcard(self, image_url: str, side: str = 'face') -> Dict[str, Any]:
        """
        通过URL识别身份证信息
        
        Args:
            image_url: 图片URL地址
            side: 身份证面，'face'为正面，'back'为反面
            
        Returns:
            Dict[str, Any]: 识别结果
        """
        if not self._client:
            return {
                'success': False,
                'message': '阿里云OCR服务未配置，请检查AccessKey配置'
            }
        
        try:
            from urllib.request import urlopen
            image_data = urlopen(image_url).read()
            image_stream = io.BytesIO(image_data)
            
            request = RecognizeIdentityCardAdvanceRequest(
                image_urlobject=image_stream,
                side=side
            )
            
            runtime = RuntimeOptions()
            response = self._client.recognize_identity_card_advance(request, runtime)
            
            if response.body and response.body.data:
                data = response.body.data
                parsed = self._parse_idcard_result(data, side)
                logger.info(f"OCR识别成功: side={side}, result={parsed}")
                return {
                    'success': True,
                    'message': '识别成功',
                    'data': parsed
                }
            else:
                logger.error(f"OCR识别失败: 无返回数据")
                return {
                    'success': False,
                    'message': 'OCR识别失败，请检查图片是否清晰'
                }
                
        except Exception as e:
            error_msg = str(e)
            if hasattr(e, 'code'):
                error_msg = f"{e.code}: {error_msg}"
            logger.error(f"OCR识别异常: {error_msg}", exc_info=True)
            return {
                'success': False,
                'message': f'识别异常: {error_msg}'
            }
    
    def _parse_idcard_result(self, data, side: str) -> Dict[str, Any]:
        """
        解析身份证识别结果
        
        Args:
            data: 阿里云返回的数据对象
            side: 身份证面
            
        Returns:
            Dict[str, Any]: 解析后的结果
        """
        result = {}
        
        if side == 'face':
            front_data = data.front_result if hasattr(data, 'front_result') else None
            if front_data:
                birth_date = front_data.birth_date or ''
                if birth_date and len(birth_date) == 8:
                    birth_date = f"{birth_date[:4]}-{birth_date[4:6]}-{birth_date[6:8]}"
                result = {
                    'name': front_data.name or '',
                    'gender': front_data.gender or '',
                    'nationality': front_data.nationality or '',
                    'birthDate': birth_date,
                    'address': front_data.address or '',
                    'idCardNumber': front_data.idnumber or ''
                }
            else:
                logger.warning(f"正面识别结果为空")
        else:
            back_data = data.back_result if hasattr(data, 'back_result') else None
            if back_data:
                start_date = back_data.start_date or ''
                end_date = back_data.end_date or ''
                if start_date and len(start_date) == 8:
                    start_date = f"{start_date[:4]}.{start_date[4:6]}.{start_date[6:8]}"
                if end_date and len(end_date) == 8:
                    end_date = f"{end_date[:4]}.{end_date[4:6]}.{end_date[6:8]}"
                valid_period = f"{start_date}-{end_date}" if start_date and end_date else (start_date or end_date)
                result = {
                    'issuingAuthority': back_data.issue or '',
                    'validPeriod': valid_period
                }
            else:
                logger.warning(f"反面识别结果为空")
        
        return result


def get_ocr_service() -> AliyunOCRService:
    """
    获取OCR服务实例
    
    Returns:
        AliyunOCRService: OCR服务实例
    """
    return AliyunOCRService()
