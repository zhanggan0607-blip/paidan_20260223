# -*- coding: utf-8 -*-
"""
Tesseract OCR身份证识别服务
作为阿里云OCR的备用引擎
"""

import base64
import io
import logging
import os
import re
import tempfile
from typing import Optional, Dict, Any

import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)


class TesseractOCRService:
    """
    Tesseract OCR身份证识别服务类
    
    作为阿里云OCR的备用引擎，支持离线识别
    """
    
    _instance: Optional['TesseractOCRService'] = None
    _tesseract_path: Optional[str] = None
    _available: bool = False
    
    def __new__(cls):
        """
        单例模式，确保只有一个实例
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        初始化Tesseract OCR
        """
        if self._tesseract_path is None:
            self._check_tesseract_available()
    
    def _check_tesseract_available(self) -> bool:
        """
        检查Tesseract是否可用
        
        Returns:
            bool: Tesseract是否可用
        """
        try:
            tesseract_cmd = os.environ.get('TESSERACT_CMD', 'tesseract')
            
            if os.name == 'nt':
                possible_paths = [
                    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                    os.path.join(os.environ.get('PROGRAMFILES', ''), 'Tesseract-OCR', 'tesseract.exe'),
                    os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Tesseract-OCR', 'tesseract.exe'),
                ]
                for path in possible_paths:
                    if os.path.exists(path):
                        tesseract_cmd = path
                        break
            
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            
            version = pytesseract.get_tesseract_version()
            self._tesseract_path = tesseract_cmd
            self._available = True
            logger.info(f"Tesseract OCR初始化成功，版本: {version}, 路径: {tesseract_cmd}")
            return True
            
        except Exception as e:
            logger.warning(f"Tesseract OCR不可用: {str(e)}")
            self._available = False
            return False
    
    def is_available(self) -> bool:
        """
        检查OCR服务是否可用
        
        Returns:
            bool: 是否可用
        """
        return self._available
    
    def recognize_idcard_base64(self, image_base64: str, side: str = 'face') -> Dict[str, Any]:
        """
        通过Base64编码识别身份证信息
        
        Args:
            image_base64: 图片Base64编码（不含data:image前缀）
            side: 身份证面，'face'为正面，'back'为反面
            
        Returns:
            Dict[str, Any]: 识别结果
        """
        if not self._available:
            return {
                'success': False,
                'message': 'Tesseract OCR服务不可用'
            }
        
        try:
            image_bytes = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_bytes))
            
            if side == 'face':
                result = self._recognize_front(image)
            else:
                result = self._recognize_back(image)
            
            logger.info(f"Tesseract OCR识别成功: side={side}")
            return {
                'success': True,
                'message': '识别成功',
                'data': result
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Tesseract OCR识别异常: {error_msg}", exc_info=True)
            return {
                'success': False,
                'message': f'识别异常: {error_msg}'
            }
    
    def _recognize_front(self, image: Image.Image) -> Dict[str, Any]:
        """
        识别身份证正面
        
        Args:
            image: PIL Image对象
            
        Returns:
            Dict[str, Any]: 识别结果
        """
        try:
            text = pytesseract.image_to_string(image, lang='chi_sim+eng', config='--psm 6')
            
            result = {
                'name': '',
                'gender': '',
                'nationality': '',
                'birthDate': '',
                'address': '',
                'idCardNumber': ''
            }
            
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            for line in lines:
                id_match = re.search(r'(\d{17}[\dXx])', line)
                if id_match:
                    result['idCardNumber'] = id_match.group(1).upper()
                    continue
                
                if '姓名' in line or '姓 名' in line:
                    name = re.sub(r'姓\s*名', '', line).strip()
                    if name:
                        result['name'] = name
                    continue
                
                if '性别' in line or '男' in line or '女' in line:
                    if '男' in line:
                        result['gender'] = '男'
                    elif '女' in line:
                        result['gender'] = '女'
                    
                    nation_match = re.search(r'民族\s*(\S+)|(\S+)\s*族', line)
                    if nation_match:
                        result['nationality'] = nation_match.group(1) or nation_match.group(2)
                    continue
                
                if '出生' in line or re.search(r'\d{4}年\d{1,2}月\d{1,2}日', line):
                    date_match = re.search(r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', line)
                    if date_match:
                        result['birthDate'] = f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"
                    continue
                
                if '住址' in line or '地址' in line:
                    addr = re.sub(r'住\s*址|地\s*址', '', line).strip()
                    if addr:
                        result['address'] = addr
                    continue
            
            if not result['name'] and lines:
                for line in lines[:3]:
                    if len(line) >= 2 and len(line) <= 10 and not any(c.isdigit() for c in line):
                        if '姓名' not in line and '性别' not in line and '民族' not in line:
                            result['name'] = line
                            break
            
            return result
            
        except Exception as e:
            logger.error(f"Tesseract正面识别失败: {str(e)}")
            return {
                'name': '',
                'gender': '',
                'nationality': '',
                'birthDate': '',
                'address': '',
                'idCardNumber': ''
            }
    
    def _recognize_back(self, image: Image.Image) -> Dict[str, Any]:
        """
        识别身份证反面
        
        Args:
            image: PIL Image对象
            
        Returns:
            Dict[str, Any]: 识别结果
        """
        try:
            text = pytesseract.image_to_string(image, lang='chi_sim+eng', config='--psm 6')
            
            result = {
                'issuingAuthority': '',
                'validPeriod': ''
            }
            
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            for line in lines:
                if '签发机关' in line:
                    authority = re.sub(r'签\s*发\s*机\s*关', '', line).strip()
                    if authority:
                        result['issuingAuthority'] = authority
                    continue
                
                date_match = re.search(r'(\d{4})[.\-年](\d{2})[.\-月](\d{2})[日]?\s*[-—至]\s*(\d{4})[.\-年\.]?(\d{2})[.\-月\.]?(\d{2})?', line)
                if date_match:
                    start_date = f"{date_match.group(1)}.{date_match.group(2)}.{date_match.group(3)}"
                    end_date = f"{date_match.group(4)}.{date_match.group(5)}.{date_match.group(6)}" if date_match.group(4) else ''
                    result['validPeriod'] = f"{start_date}-{end_date}" if end_date else start_date
                    continue
                
                if '有效期' in line:
                    period = re.sub(r'有\s*效\s*期\s*限', '', line).strip()
                    if period and not result['validPeriod']:
                        result['validPeriod'] = period
                    continue
            
            return result
            
        except Exception as e:
            logger.error(f"Tesseract反面识别失败: {str(e)}")
            return {
                'issuingAuthority': '',
                'validPeriod': ''
            }


def get_tesseract_ocr_service() -> TesseractOCRService:
    """
    获取Tesseract OCR服务实例
    
    Returns:
        TesseractOCRService: OCR服务实例
    """
    return TesseractOCRService()
