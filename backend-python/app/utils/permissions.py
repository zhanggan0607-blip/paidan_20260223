# -*- coding: utf-8 -*-
"""
权限控制装饰器
提供统一的权限校验功能
"""

from functools import wraps
from typing import List, Optional, Callable
from fastapi import HTTPException, status, Depends
from app.auth import get_current_user_required
from app.utils.permission_config import (
    MANAGER_ROLES,
    ADMIN_ROLES,
    has_permission,
    is_manager_role,
    is_admin_role,
    get_role_level,
)


def require_roles(*required_roles: str):
    """
    角色权限装饰器
    
    用于限制API只能被特定角色的用户访问
    
    Args:
        *required_roles: 允许访问的角色列表
        
    Usage:
        @router.get("/admin-only")
        @require_roles('管理员', '部门经理')
        async def admin_endpoint(current_user: dict = Depends(get_current_user_required)):
            return {"message": "admin access"}
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, current_user: dict = Depends(get_current_user_required), **kwargs):
            user_role = current_user.get('role', '')
            if user_role not in required_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"权限不足，需要以下角色之一: {', '.join(required_roles)}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, current_user: dict = Depends(get_current_user_required), **kwargs):
            user_role = current_user.get('role', '')
            if user_role not in required_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"权限不足，需要以下角色之一: {', '.join(required_roles)}"
                )
            return func(*args, current_user=current_user, **kwargs)
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def require_manager(func: Callable):
    """
    管理员/经理权限装饰器
    
    限制只有管理员、部门经理、主管可以访问
    
    Usage:
        @router.get("/manager-only")
        @require_manager
        async def manager_endpoint(current_user: dict = Depends(get_current_user_required)):
            return {"message": "manager access"}
    """
    return require_roles(*MANAGER_ROLES)(func)


def require_admin(func: Callable):
    """
    管理员权限装饰器
    
    限制只有管理员可以访问
    
    Usage:
        @router.delete("/admin-only")
        @require_admin
        async def admin_endpoint(current_user: dict = Depends(get_current_user_required)):
            return {"message": "admin access"}
    """
    return require_roles(*ADMIN_ROLES)(func)


def check_permission(current_user: Optional[dict], required_roles: List[str]) -> bool:
    """
    检查用户是否有指定权限
    
    Args:
        current_user: 当前用户信息
        required_roles: 需要的角色列表
        
    Returns:
        bool: 是否有权限
    """
    if not current_user:
        return False
    
    user_role = current_user.get('role', '')
    return user_role in required_roles


def is_manager(current_user: Optional[dict]) -> bool:
    """
    检查用户是否为管理员/经理
    
    Args:
        current_user: 当前用户信息
        
    Returns:
        bool: 是否为管理员/经理
    """
    if not current_user:
        return False
    return is_manager_role(current_user.get('role', ''))


def is_admin(current_user: Optional[dict]) -> bool:
    """
    检查用户是否为管理员
    
    Args:
        current_user: 当前用户信息
        
    Returns:
        bool: 是否为管理员
    """
    if not current_user:
        return False
    return is_admin_role(current_user.get('role', ''))


def get_user_role(current_user: Optional[dict]) -> str:
    """
    获取用户角色
    
    Args:
        current_user: 当前用户信息
        
    Returns:
        str: 用户角色，未登录返回空字符串
    """
    if not current_user:
        return ''
    return current_user.get('role', '')


def check_user_permission(current_user: Optional[dict], permission_id: str) -> bool:
    """
    检查用户是否有指定权限
    
    Args:
        current_user: 当前用户信息
        permission_id: 权限ID
        
    Returns:
        bool: 是否有权限
    """
    if not current_user:
        return False
    return has_permission(current_user.get('role', ''), permission_id)


def get_user_role_level(current_user: Optional[dict]) -> int:
    """
    获取用户角色级别
    
    Args:
        current_user: 当前用户信息
        
    Returns:
        int: 角色级别，级别越高权限越大
    """
    if not current_user:
        return 0
    return get_role_level(current_user.get('role', ''))
