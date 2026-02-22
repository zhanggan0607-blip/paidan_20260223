"""
密码安全工具模块
提供密码哈希和验证功能
"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    生成密码哈希值
    
    Args:
        password: 明文密码
        
    Returns:
        str: 哈希后的密码
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否匹配
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希后的密码
        
    Returns:
        bool: 密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_default_password(phone: str = None) -> str:
    """
    获取默认密码（手机号后6位，无手机号则为123456）
    
    Args:
        phone: 手机号
        
    Returns:
        str: 默认密码
    """
    if phone and len(phone) >= 6:
        return phone[-6:]
    return "123456"
