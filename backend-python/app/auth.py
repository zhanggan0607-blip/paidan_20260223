"""
认证模块
提供JWT Token生成和验证功能

安全说明：
- 所有认证必须通过JWT Token完成
- 密码使用bcrypt加密存储
"""
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

settings = get_settings()
SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码与哈希密码是否匹配

    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码

    Returns:
        是否匹配
    """
    truncated_password = plain_password[:72]
    return pwd_context.verify(truncated_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    生成密码的哈希值

    Args:
        password: 明文密码

    Returns:
        哈希密码
    """
    truncated_password = password[:72]
    return pwd_context.hash(truncated_password)


def create_access_token(data: dict) -> str:
    """
    创建JWT访问令牌

    Args:
        data: 要编码的数据

    Returns:
        JWT Token字符串
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str | None = Depends(oauth2_scheme)) -> dict | None:
    """
    从JWT Token获取当前用户信息（可选认证）

    Args:
        token: JWT Token

    Returns:
        用户信息字典，未认证返回None
    """
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user_required(token: str = Depends(oauth2_scheme)) -> dict:
    """
    从JWT Token获取当前用户信息（必须认证）

    Args:
        token: JWT Token

    Returns:
        用户信息字典

    Raises:
        HTTPException: 未认证时抛出401异常
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="未登录或登录已过期，请重新登录",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise credentials_exception from e


async def get_current_admin_user(
    request: Request,
    current_user: dict | None = Depends(get_current_user)
) -> dict:
    """
    获取当前管理员用户，非管理员会抛出403异常

    Args:
        request: FastAPI请求对象
        current_user: 当前用户信息

    Returns:
        用户信息字典

    Raises:
        HTTPException: 未认证抛出401，权限不足抛出403
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或登录已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )

    role = current_user.get('role', '')
    if role not in ['管理员', '部门经理', '主管']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )

    return current_user
