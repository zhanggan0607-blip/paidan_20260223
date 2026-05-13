"""
Service基类
提供统一的事务管理和通用方法
"""
from app.utils.logging_config import get_logger
from typing import TypeVar

from sqlalchemy.orm import Session

logger = get_logger(__name__)

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
        try:
            self._db.commit()
            logger.debug("事务已提交")
        except Exception as e:
            logger.error(f"事务提交失败: {str(e)}")
            self._db.rollback()
            raise
    
    def rollback(self) -> None:
        try:
            self._db.rollback()
            logger.debug("事务已回滚")
        except Exception as e:
            logger.error(f"事务回滚失败: {str(e)}")
    
    def flush(self) -> None:
        try:
            self._db.flush()
        except Exception as e:
            logger.error(f"flush失败: {str(e)}")
            self._db.rollback()
            raise
    
    def execute_in_transaction(self, func, *args, **kwargs):
        try:
            result = func(*args, **kwargs)
            self.commit()
            return result
        except Exception as e:
            self.rollback()
            raise

    def _create_operation_log(
        self,
        work_order_type: str,
        work_order_id: int,
        work_order_no: str,
        operator_name: str,
        operator_id: int | None,
        operation_type: str,
        operation_type_name: str,
        remark: str
    ) -> None:
        from app.models.work_order_operation_log import WorkOrderOperationLog

        log = WorkOrderOperationLog(
            work_order_type=work_order_type,
            work_order_id=work_order_id,
            work_order_no=work_order_no,
            operator_name=operator_name,
            operator_id=operator_id,
            operation_type=operation_type,
            operation_type_code=operation_type,
            operation_type_name=operation_type_name,
            operation_remark=remark
        )
        self._db.add(log)
        self._db.flush()
