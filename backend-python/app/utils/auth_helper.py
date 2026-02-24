"""
用户上下文工具
统一管理用户信息提取和权限判断逻辑
"""
from typing import Optional, Tuple, Dict, Any
from fastapi import Request
from dataclasses import dataclass


@dataclass
class UserContext:
    """
    用户上下文数据类
    封装用户信息和权限判断结果
    """
    user_name: Optional[str]
    is_manager: bool
    user_info: Optional[Dict[str, Any]] = None
    
    @property
    def is_authenticated(self) -> bool:
        """是否已认证"""
        return self.user_name is not None


MANAGER_ROLES = ['管理员', '部门经理', '主管']


def get_current_user_from_headers(request: Request) -> Optional[Dict[str, Any]]:
    """
    从请求头获取当前用户信息
    
    Args:
        request: FastAPI 请求对象
        
    Returns:
        用户信息字典，未找到返回 None
    """
    user_info = request.headers.get('X-User-Info')
    if user_info:
        import json
        try:
            return json.loads(user_info)
        except json.JSONDecodeError:
            pass
    return None


def get_user_context(
    request: Request,
    current_user: Optional[Dict[str, Any]] = None
) -> UserContext:
    """
    获取用户上下文
    
    Args:
        request: FastAPI 请求对象
        current_user: 当前用户信息（可选）
        
    Returns:
        UserContext 实例
    """
    user_info = current_user or get_current_user_from_headers(request)
    
    if not user_info:
        return UserContext(user_name=None, is_manager=False, user_info=None)
    
    user_name = user_info.get('sub') or user_info.get('name')
    role = user_info.get('role', '')
    is_manager = role in MANAGER_ROLES
    
    return UserContext(
        user_name=user_name,
        is_manager=is_manager,
        user_info=user_info
    )


def get_user_name_and_role(
    request: Request,
    current_user: Optional[Dict[str, Any]] = None
) -> Tuple[Optional[str], bool]:
    """
    获取用户名和是否为管理员
    
    Args:
        request: FastAPI 请求对象
        current_user: 当前用户信息（可选）
        
    Returns:
        (用户名, 是否为管理员) 元组
    """
    context = get_user_context(request, current_user)
    return context.user_name, context.is_manager


def is_user_manager(
    request: Request,
    current_user: Optional[Dict[str, Any]] = None
) -> bool:
    """
    判断用户是否为管理员
    
    Args:
        request: FastAPI 请求对象
        current_user: 当前用户信息（可选）
        
    Returns:
        是否为管理员
    """
    context = get_user_context(request, current_user)
    return context.is_manager


def get_user_name(
    request: Request,
    current_user: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    获取用户名
    
    Args:
        request: FastAPI 请求对象
        current_user: 当前用户信息（可选）
        
    Returns:
        用户名
    """
    context = get_user_context(request, current_user)
    return context.user_name
