# -*- coding: utf-8 -*-
"""
OCR服务管理器
支持主备切换、缓存机制
"""

import hashlib
import logging
import threading
import time
from typing import Dict, Any, Optional

from app.utils.aliyun_ocr import AliyunOCRService
from app.utils.tesseract_ocr import TesseractOCRService

logger = logging.getLogger(__name__)


class OCRServiceManager:
    """
    OCR服务管理器
    
    支持多引擎主备切换和结果缓存
    """
    
    _instance: Optional['OCRServiceManager'] = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """
        单例模式
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        初始化OCR服务管理器
        """
        if not hasattr(self, '_initialized'):
            self._aliyun_ocr = AliyunOCRService()
            self._tesseract_ocr = TesseractOCRService()
            self._cache: Dict[str, Dict[str, Any]] = {}
            self._cache_lock = threading.Lock()
            self._cache_ttl = 7 * 24 * 60 * 60
            self._initialized = True
            logger.info("OCR服务管理器初始化完成")
    
    def _get_image_hash(self, image_base64: str, side: str) -> str:
        """
        计算图片哈希值用于缓存
        
        Args:
            image_base64: 图片Base64编码
            side: 身份证面
            
        Returns:
            str: 哈希值
        """
        content = f"{image_base64[:100]}_{side}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        获取缓存结果
        
        Args:
            cache_key: 缓存键
            
        Returns:
            Optional[Dict[str, Any]]: 缓存结果或None
        """
        with self._cache_lock:
            cached = self._cache.get(cache_key)
            if cached:
                if time.time() - cached['timestamp'] < self._cache_ttl:
                    logger.debug(f"OCR缓存命中: {cache_key[:16]}...")
                    return cached['result']
                else:
                    del self._cache[cache_key]
            return None
    
    def _set_cached_result(self, cache_key: str, result: Dict[str, Any]):
        """
        设置缓存结果
        
        Args:
            cache_key: 缓存键
            result: 识别结果
        """
        with self._cache_lock:
            self._cache[cache_key] = {
                'result': result,
                'timestamp': time.time()
            }
            logger.debug(f"OCR结果已缓存: {cache_key[:16]}...")
            
            if len(self._cache) > 1000:
                self._cleanup_cache()
    
    def _cleanup_cache(self):
        """
        清理过期缓存
        """
        current_time = time.time()
        expired_keys = [
            k for k, v in self._cache.items()
            if current_time - v['timestamp'] > self._cache_ttl
        ]
        for key in expired_keys:
            del self._cache[key]
        logger.info(f"清理了{len(expired_keys)}个过期OCR缓存")
    
    def recognize_idcard_base64(self, image_base64: str, side: str = 'face') -> Dict[str, Any]:
        """
        识别身份证（Base64图片）
        
        优先使用阿里云OCR，失败时降级到Tesseract
        
        Args:
            image_base64: 图片Base64编码
            side: 身份证面
            
        Returns:
            Dict[str, Any]: 识别结果
        """
        cache_key = self._get_image_hash(image_base64, side)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            cached_result['from_cache'] = True
            return cached_result
        
        if self._aliyun_ocr.is_configured():
            logger.info("使用阿里云OCR引擎")
            result = self._aliyun_ocr.recognize_idcard_base64(image_base64, side)
            if result['success']:
                result['engine'] = 'aliyun'
                self._set_cached_result(cache_key, result)
                return result
            else:
                logger.warning(f"阿里云OCR识别失败，尝试降级到Tesseract: {result['message']}")
        
        if self._tesseract_ocr.is_available():
            logger.info("使用Tesseract OCR引擎（备用）")
            result = self._tesseract_ocr.recognize_idcard_base64(image_base64, side)
            if result['success']:
                result['engine'] = 'tesseract'
                self._set_cached_result(cache_key, result)
                return result
            else:
                logger.error(f"Tesseract OCR识别也失败: {result['message']}")
        
        return {
            'success': False,
            'message': '所有OCR引擎都不可用或识别失败',
            'engine': None
        }
    
    def recognize_idcard_url(self, image_url: str, side: str = 'face') -> Dict[str, Any]:
        """
        识别身份证（URL图片）
        
        Args:
            image_url: 图片URL
            side: 身份证面
            
        Returns:
            Dict[str, Any]: 识别结果
        """
        if self._aliyun_ocr.is_configured():
            logger.info("使用阿里云OCR引擎")
            result = self._aliyun_ocr.recognize_idcard(image_url, side)
            if result['success']:
                result['engine'] = 'aliyun'
                return result
            else:
                logger.warning(f"阿里云OCR识别失败: {result['message']}")
        
        try:
            from urllib.request import urlopen
            image_data = urlopen(image_url).read()
            import base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            return self.recognize_idcard_base64(image_base64, side)
        except Exception as e:
            logger.error(f"下载图片失败: {str(e)}")
            return {
                'success': False,
                'message': f'下载图片失败: {str(e)}',
                'engine': None
            }
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取OCR服务状态
        
        Returns:
            Dict[str, Any]: 服务状态
        """
        return {
            'aliyun': {
                'available': self._aliyun_ocr.is_configured(),
                'type': 'primary'
            },
            'tesseract': {
                'available': self._tesseract_ocr.is_available(),
                'type': 'fallback'
            },
            'cache': {
                'enabled': True,
                'count': len(self._cache),
                'ttl_seconds': self._cache_ttl
            }
        }


def get_ocr_manager() -> OCRServiceManager:
    """
    获取OCR服务管理器实例
    
    Returns:
        OCRServiceManager: 服务管理器实例
    """
    return OCRServiceManager()
