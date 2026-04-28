"""
Service基类
提供统一的事务管理和通用方法
"""
import logging
from typing import TypeVar

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

T = TypeVar('T')


class BaseService:
    """
    Service基类
    
    提供统一的事务管理：
    - 所有写操作（create/update/delete）后需要调用commit()提交事务
    - 异常时自动回滚
    - Repository层只执行flush，不执行commit
    
    使用示例:
    class UserService(BaseService):
        def __init__(self, db: Session):
            super().__init__(db)
            self.repository = UserRepository(db)
        
        def create_user(self, dto: UserCreate) -> User:
            user = User(**dto.dict())
            self.repository.create(user)
            self.commit()
            return user
    """
    
    def __init__(self, db: Session):
        self._db = db
    
    @property
    def db(self) -> Session:
        return self._db
    
    def commit(self) -> None:
        """
        提交事务
        
        在执行完所有数据库操作后调用此方法提交事务
        """
        try:
            self._db.commit()
            logger.debug("事务已提交")
        except Exception as e:
            logger.error(f"事务提交失败: {str(e)}")
            self._db.rollback()
            raise
    
    def rollback(self) -> None:
        """
        回滚事务
        
        通常不需要手动调用，异常时会自动回滚
        """
        try:
            self._db.rollback()
            logger.debug("事务已回滚")
        except Exception as e:
            logger.error(f"事务回滚失败: {str(e)}")
    
    def flush(self) -> None:
        """
        刷新到数据库（不提交事务）
        
        用于获取自增ID等场景
        """
        try:
            self._db.flush()
        except Exception as e:
            logger.error(f"flush失败: {str(e)}")
            self._db.rollback()
            raise
    
    def execute_in_transaction(self, func, *args, **kwargs):
        """
        在事务中执行函数
        
        自动处理提交和回滚
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果
            
        Example:
            def create_user(self, dto):
                return self.execute_in_transaction(
                    lambda: self._do_create_user(dto)
                )
        """
        try:
            result = func(*args, **kwargs)
            self.commit()
            return result
        except Exception as e:
            self.rollback()
            raise
