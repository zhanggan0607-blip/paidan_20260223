"""
依赖注入模块
提供统一的依赖注入组件，包括权限控制、数据库会话等
"""
from dataclasses import dataclass
from typing import Optional, List
from urllib.parse import unquote
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import get_db

settings = get_settings()
SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

MANAGER_ROLES = ['管理员', '部门经理', '主管']


@dataclass
class UserInfo:
    """
    用户信息数据类
    封装用户信息，提供便捷的属性访问
    """
    id: Optional[int] = None
    name: Optional[str] = None
    role: Optional[str] = None
    token: Optional[str] = None
    
    @property
    def is_manager(self) -> bool:
        """判断是否为管理员角色"""
        return self.role in MANAGER_ROLES
    
    @property
    def is_admin(self) -> bool:
        """判断是否为超级管理员"""
        return self.role == '管理员'
    
    @property
    def is_authenticated(self) -> bool:
        """判断是否已认证"""
        return self.name is not None
    
    def get_maintenance_personnel_filter(self) -> Optional[str]:
        """
        获取运维人员过滤条件
        管理员返回None（不过滤），普通用户返回自己的用户名
        """
        return None if self.is_manager else self.name
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'is_manager': self.is_manager,
            'is_admin': self.is_admin
        }


def _parse_jwt_token(token: str) -> Optional[dict]:
    """
    解析JWT Token
    
    Args:
        token: JWT Token字符串
        
    Returns:
        解析后的payload，解析失败返回None
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def _extract_user_from_headers(request: Request) -> Optional[dict]:
    """
    从请求头提取用户信息
    
    Args:
        request: FastAPI请求对象
        
    Returns:
        用户信息字典，未找到返回None
    """
    user_name = request.headers.get('X-User-Name')
    user_role = request.headers.get('X-User-Role')
    
    if user_name:
        return {
            'sub': unquote(user_name),
            'name': unquote(user_name),
            'role': unquote(user_role) if user_role else '运维人员'
        }
    return None


async def get_current_user_info(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme)
) -> UserInfo:
    """
    获取当前用户信息（可选认证）
    
    优先从JWT Token获取，其次从请求头获取
    
    Args:
        request: FastAPI请求对象
        token: OAuth2 Token
        
    Returns:
        UserInfo对象
    """
    user_data = None
    
    if token:
        user_data = _parse_jwt_token(token)
    
    if not user_data:
        user_data = _extract_user_from_headers(request)
    
    if not user_data:
        return UserInfo()
    
    return UserInfo(
        id=user_data.get('id'),
        name=user_data.get('sub') or user_data.get('name'),
        role=user_data.get('role', '运维人员'),
        token=token
    )


async def get_current_user_required(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme)
) -> UserInfo:
    """
    获取当前用户信息（必须认证）
    
    未认证时抛出401异常
    
    Args:
        request: FastAPI请求对象
        token: OAuth2 Token
        
    Returns:
        UserInfo对象
        
    Raises:
        HTTPException: 未认证时抛出401异常
    """
    user_info = await get_current_user_info(request, token)
    
    if not user_info.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或登录已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_info


async def get_manager_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme)
) -> UserInfo:
    """
    获取管理员用户信息
    
    非管理员角色抛出403异常
    
    Args:
        request: FastAPI请求对象
        token: OAuth2 Token
        
    Returns:
        UserInfo对象
        
    Raises:
        HTTPException: 未认证抛出401，权限不足抛出403
    """
    user_info = await get_current_user_required(request, token)
    
    if not user_info.is_manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员或部门经理权限"
        )
    
    return user_info


async def get_admin_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme)
) -> UserInfo:
    """
    获取超级管理员用户信息
    
    非超级管理员抛出403异常
    
    Args:
        request: FastAPI请求对象
        token: OAuth2 Token
        
    Returns:
        UserInfo对象
        
    Raises:
        HTTPException: 未认证抛出401，权限不足抛出403
    """
    user_info = await get_current_user_required(request, token)
    
    if not user_info.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要超级管理员权限"
        )
    
    return user_info


def get_service_factory(service_class):
    """
    服务类工厂函数生成器
    
    用于依赖注入Service实例
    
    Args:
        service_class: Service类
        
    Returns:
        依赖函数
        
    使用示例:
        @router.get("")
        def get_list(
            service: SpotWorkService = Depends(get_service_factory(SpotWorkService))
        ):
            return service.get_list()
    """
    def get_service(db: Session = Depends(get_db)):
        return service_class(db)
    return get_service


def get_repository_factory(repository_class):
    """
    Repository类工厂函数生成器
    
    用于依赖注入Repository实例
    
    Args:
        repository_class: Repository类
        
    Returns:
        依赖函数
    """
    def get_repository(db: Session = Depends(get_db)):
        return repository_class(db)
    return get_repository
