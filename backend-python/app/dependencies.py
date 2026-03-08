"""
依赖注入模块
提供统一的依赖注入组件，包括权限控制、数据库会话等

安全说明：
- 所有认证必须通过JWT Token完成
- 不再支持请求头认证（X-User-Name/X-User-Role已被移除）
- 这是为了防止身份伪造攻击
"""
from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request, status
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

MATERIAL_MANAGER_ROLES = ['管理员', '部门经理', '材料员']


@dataclass
class UserInfo:
    """
    用户信息数据类
    封装用户信息，提供便捷的属性访问
    """
    id: int | None = None
    name: str | None = None
    role: str | None = None
    token: str | None = None

    @property
    def is_manager(self) -> bool:
        """判断是否为管理员角色"""
        return self.role in MANAGER_ROLES

    @property
    def is_admin(self) -> bool:
        """判断是否为超级管理员"""
        return self.role == '管理员'

    @property
    def is_material_manager(self) -> bool:
        """判断是否为材料管理员（包括管理员、部门经理、材料员）"""
        return self.role in MATERIAL_MANAGER_ROLES

    @property
    def is_authenticated(self) -> bool:
        """判断是否已认证"""
        return self.name is not None and self.token is not None

    def get_maintenance_personnel_filter(self) -> str | None:
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


def _parse_jwt_token(token: str) -> dict | None:
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


async def get_current_user_info(
    request: Request,
    token: str | None = Depends(oauth2_scheme)
) -> UserInfo:
    """
    获取当前用户信息（可选认证）

    仅通过JWT Token获取用户信息

    Args:
        request: FastAPI请求对象
        token: OAuth2 Token

    Returns:
        UserInfo对象
    """
    if not token:
        return UserInfo()

    user_data = _parse_jwt_token(token)

    if not user_data:
        return UserInfo()

    return UserInfo(
        id=user_data.get('user_id') or user_data.get('id'),
        name=user_data.get('sub') or user_data.get('name'),
        role=user_data.get('role', '运维人员'),
        token=token
    )


async def get_current_user_required(
    request: Request,
    token: str | None = Depends(oauth2_scheme)
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
            detail="未登录或登录已过期，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_info


async def get_manager_user(
    request: Request,
    token: str | None = Depends(oauth2_scheme)
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
    token: str | None = Depends(oauth2_scheme)
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


async def get_material_manager_user(
    request: Request,
    token: str | None = Depends(oauth2_scheme)
) -> UserInfo:
    """
    获取材料管理员用户信息

    材料管理员包括：管理员、部门经理、材料员
    非材料管理员抛出403异常

    Args:
        request: FastAPI请求对象
        token: OAuth2 Token

    Returns:
        UserInfo对象

    Raises:
        HTTPException: 未认证抛出401，权限不足抛出403
    """
    user_info = await get_current_user_required(request, token)

    if not user_info.is_material_manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员、部门经理或材料员权限"
        )

    return user_info


def check_data_access(user_info: UserInfo, data_owner: str) -> bool:
    """
    检查用户是否有权访问某条数据

    Args:
        user_info: 用户信息
        data_owner: 数据所有者用户名

    Returns:
        是否有权访问
    """
    if user_info.is_manager:
        return True
    return user_info.name == data_owner


def assert_data_owner_or_manager(user_info: UserInfo, data_owner: str) -> None:
    """
    断言用户是数据所有者或管理员

    Args:
        user_info: 用户信息
        data_owner: 数据所有者用户名

    Raises:
        HTTPException: 权限不足时抛出403异常
    """
    if not check_data_access(user_info, data_owner):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此数据"
        )
