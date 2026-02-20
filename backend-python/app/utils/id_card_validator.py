# -*- coding: utf-8 -*-
"""
身份证号码强认证工具
包含格式验证、校验码验证、出生日期验证、性别验证
"""

from typing import Tuple, Optional
from datetime import datetime


WEIGHTS = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
CHECK_CODES = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']


def validate_id_card(id_card: str) -> Tuple[bool, str, Optional[str], Optional[str]]:
    """
    验证身份证号码
    
    Args:
        id_card: 身份证号码
        
    Returns:
        Tuple[是否有效, 错误信息/成功信息, 出生日期, 性别]
    """
    if not id_card:
        return False, '身份证号码不能为空', None, None
    
    id_card = id_card.upper().strip()
    
    if len(id_card) != 18:
        return False, '身份证号码必须为18位', None, None
    
    import re
    if not re.match(r'^\d{17}[\dX]$', id_card):
        return False, '身份证号码格式不正确，前17位必须为数字，最后一位可以是数字或X', None, None
    
    total = 0
    for i in range(17):
        total += int(id_card[i]) * WEIGHTS[i]
    check_code = CHECK_CODES[total % 11]
    
    if id_card[17] != check_code:
        return False, '身份证号码校验码错误，请检查是否输入正确', None, None
    
    try:
        year = int(id_card[6:10])
        month = int(id_card[10:12])
        day = int(id_card[12:14])
    except ValueError:
        return False, '身份证号码中日期格式错误', None, None
    
    birth_date = f"{year}-{month:02d}-{day:02d}"
    
    if month < 1 or month > 12:
        return False, '身份证号码中月份无效，应为01-12', None, None
    
    import calendar
    _, days_in_month = calendar.monthrange(year, month)
    if day < 1 or day > days_in_month:
        return False, f'身份证号码中日期无效，{year}年{month}月没有{day}日', None, None
    
    try:
        birth_date_obj = datetime(year, month, day)
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if birth_date_obj > today:
            return False, '身份证号码中出生日期不能晚于今天', None, None
    except ValueError as e:
        return False, f'身份证号码中出生日期无效: {str(e)}', None, None
    
    min_year = 1900
    if year < min_year:
        return False, f'身份证号码中出生年份不能早于{min_year}年', None, None
    
    gender_code = int(id_card[16:17])
    gender = '男' if gender_code % 2 == 1 else '女'
    
    return True, '身份证号码验证通过', birth_date, gender


def extract_birth_date(id_card: str) -> Optional[str]:
    """
    从身份证号码提取出生日期
    
    Args:
        id_card: 身份证号码
        
    Returns:
        出生日期字符串 (YYYY-MM-DD格式) 或 None
    """
    if not id_card or len(id_card) != 18:
        return None
    
    year = id_card[6:10]
    month = id_card[10:12]
    day = id_card[12:14]
    
    return f"{year}-{month}-{day}"


def extract_gender(id_card: str) -> Optional[str]:
    """
    从身份证号码提取性别
    
    Args:
        id_card: 身份证号码
        
    Returns:
        性别 ('男' 或 '女') 或 None
    """
    if not id_card or len(id_card) != 18:
        return None
    
    gender_code = int(id_card[16:17])
    return '男' if gender_code % 2 == 1 else '女'


def calculate_age(birth_date: str) -> Optional[int]:
    """
    计算年龄
    
    Args:
        birth_date: 出生日期字符串 (YYYY-MM-DD格式)
        
    Returns:
        年龄 或 None
    """
    if not birth_date:
        return None
    
    try:
        birth = datetime.strptime(birth_date, '%Y-%m-%d')
        today = datetime.now()
        
        age = today.year - birth.year
        if (today.month, today.day) < (birth.month, birth.day):
            age -= 1
        
        return age if age >= 0 else None
    except ValueError:
        return None
