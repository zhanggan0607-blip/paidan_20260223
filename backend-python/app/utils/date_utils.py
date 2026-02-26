"""
日期解析工具模块
提供统一的日期解析和格式化功能
"""
from datetime import datetime, date
from typing import Optional, Union


def parse_date(date_value: Optional[Union[str, date, datetime]]) -> Optional[date]:
    """
    统一的日期解析方法
    
    Args:
        date_value: 日期值，可以是字符串、date对象或datetime对象
        
    Returns:
        解析后的date对象，解析失败返回None
    """
    if date_value is None:
        return None
    
    if isinstance(date_value, date) and not isinstance(date_value, datetime):
        return date_value
    
    if isinstance(date_value, datetime):
        return date_value.date()
    
    if isinstance(date_value, str):
        date_str = date_value.strip()
        if not date_str:
            return None
        
        date_formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%Y年%m月%d日',
            '%d/%m/%Y',
            '%m/%d/%Y',
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        try:
            iso_date = date_str.split('T')[0]
            return datetime.strptime(iso_date, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    return None


def parse_datetime(datetime_value: Optional[Union[str, datetime]]) -> Optional[datetime]:
    """
    统一的日期时间解析方法
    
    Args:
        datetime_value: 日期时间值，可以是字符串或datetime对象
        
    Returns:
        解析后的datetime对象，解析失败返回None
    """
    if datetime_value is None:
        return None
    
    if isinstance(datetime_value, datetime):
        return datetime_value
    
    if isinstance(datetime_value, str):
        datetime_str = datetime_value.strip()
        if not datetime_str:
            return None
        
        datetime_formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y/%m/%d %H:%M:%S',
            '%Y-%m-%d',
        ]
        
        for fmt in datetime_formats:
            try:
                return datetime.strptime(datetime_str, fmt)
            except ValueError:
                continue
    
    return None


def format_date(date_value: Optional[Union[str, date, datetime]], fmt: str = '%Y-%m-%d') -> Optional[str]:
    """
    格式化日期为字符串
    
    Args:
        date_value: 日期值
        fmt: 输出格式，默认为YYYY-MM-DD
        
    Returns:
        格式化后的日期字符串
    """
    parsed = parse_date(date_value)
    if parsed:
        return parsed.strftime(fmt)
    return None


def format_datetime(datetime_value: Optional[Union[str, datetime]], fmt: str = '%Y-%m-%d %H:%M:%S') -> Optional[str]:
    """
    格式化日期时间为字符串
    
    Args:
        datetime_value: 日期时间值
        fmt: 输出格式，默认为YYYY-MM-DD HH:MM:SS
        
    Returns:
        格式化后的日期时间字符串
    """
    parsed = parse_datetime(datetime_value)
    if parsed:
        return parsed.strftime(fmt)
    return None
