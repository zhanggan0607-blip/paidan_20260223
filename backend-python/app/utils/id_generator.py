"""
ID 生成工具
统一管理各种编号的生成逻辑
"""
import random
import string
from datetime import datetime
from typing import Optional


def generate_order_no(prefix: str, project_no: Optional[str] = None) -> str:
    """
    生成工单编号
    
    编号规则：前缀 + 项目编号 + 年月日 + 随机数
    格式：XX-XXXX0X-XXXXXX0X
    
    Args:
        prefix: 编号前缀（如 XJ、WX、YG）
        project_no: 项目编号（可选）
        
    Returns:
        生成的工单编号
    """
    date_str = datetime.now().strftime('%Y%m%d')
    random_suffix = ''.join(random.choices(string.digits, k=2))
    
    if project_no:
        return f"{prefix}-{project_no}-{date_str}{random_suffix}"
    else:
        return f"{prefix}-{date_str}{random_suffix}"


def generate_inspection_id(project_no: Optional[str] = None) -> str:
    """
    生成定期巡检单编号
    
    Args:
        project_no: 项目编号（可选）
        
    Returns:
        巡检单编号
    """
    return generate_order_no('XJ', project_no)


def generate_repair_id(project_no: Optional[str] = None) -> str:
    """
    生成临时维修单编号
    
    Args:
        project_no: 项目编号（可选）
        
    Returns:
        维修单编号
    """
    return generate_order_no('WX', project_no)


def generate_work_id(project_no: Optional[str] = None) -> str:
    """
    生成零星用工单编号
    
    Args:
        project_no: 项目编号（可选）
        
    Returns:
        用工单编号
    """
    return generate_order_no('YG', project_no)


def generate_inbound_no(prefix: str = 'RK') -> str:
    """
    生成入库单号
    
    Args:
        prefix: 编号前缀（默认 RK）
        
    Returns:
        入库单号
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{timestamp}{random_str}"


def generate_outbound_no(prefix: str = 'CK') -> str:
    """
    生成出库单号
    
    Args:
        prefix: 编号前缀（默认 CK）
        
    Returns:
        出库单号
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{timestamp}{random_str}"


def generate_plan_id(plan_type: str) -> str:
    """
    生成计划编号
    
    Args:
        plan_type: 计划类型
        
    Returns:
        计划编号
    """
    type_prefix_map = {
        '定期巡检': 'XJJH',
        '临时维修': 'WXJH',
        '零星用工': 'YGJH',
        '定期维保': 'WBJH'
    }
    
    prefix = type_prefix_map.get(plan_type, 'JH')
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.digits, k=3))
    return f"{prefix}{timestamp}{random_str}"
