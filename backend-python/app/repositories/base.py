"""
Repository 基类
提供通用的 CRUD 操作方法，减少代码重复
"""
from typing import TypeVar, Generic, Type, List, Optional, Any
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    Repository 基类
    提供通用的数据库操作方法
    
    使用示例:
    class PeriodicInspectionRepository(BaseRepository[PeriodicInspection]):
        def __init__(self, db: Session):
            super().__init__(db, PeriodicInspection)
    """
    
    def __init__(self, db: Session, model_class: Type[T]):
        """
        初始化 Repository
        
        Args:
            db: 数据库会话
            model_class: 模型类
        """
        self._db = db
        self._model_class = model_class
    
    @property
    def db(self) -> Session:
        """获取数据库会话"""
        return self._db
    
    @property
    def model_class(self) -> Type[T]:
        """获取模型类"""
        return self._model_class
    
    def find_by_id(self, id: int, options: Optional[list] = None) -> Optional[T]:
        """
        根据 ID 查询实体
        
        Args:
            id: 实体 ID
            options: SQLAlchemy 查询选项（如 joinedload）
            
        Returns:
            查询到的实体，未找到返回 None
        """
        try:
            query = self.db.query(self.model_class)
            if options:
                for option in options:
                    query = query.options(option)
            return query.filter(self.model_class.id == id).first()
        except Exception as e:
            logger.error(f"查询{self.model_class.__name__}失败 (id={id}): {str(e)}")
            raise
    
    def find_all_unpaginated(self, options: Optional[list] = None) -> List[T]:
        """
        查询所有实体（不分页）
        
        Args:
            options: SQLAlchemy 查询选项
            
        Returns:
            实体列表
        """
        try:
            query = self.db.query(self.model_class)
            if options:
                for option in options:
                    query = query.options(option)
            return query.all()
        except Exception as e:
            logger.error(f"查询所有{self.model_class.__name__}失败: {str(e)}")
            raise
    
    def create(self, entity: T) -> T:
        """
        创建实体
        
        Args:
            entity: 要创建的实体
            
        Returns:
            创建后的实体
        """
        try:
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            return entity
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建{self.model_class.__name__}失败: {str(e)}")
            raise
    
    def update(self, entity: T) -> T:
        """
        更新实体
        
        Args:
            entity: 要更新的实体
            
        Returns:
            更新后的实体
        """
        try:
            self.db.commit()
            self.db.refresh(entity)
            return entity
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新{self.model_class.__name__}失败: {str(e)}")
            raise
    
    def delete(self, entity: T) -> None:
        """
        删除实体
        
        Args:
            entity: 要删除的实体
        """
        try:
            self.db.delete(entity)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除{self.model_class.__name__}失败: {str(e)}")
            raise
    
    def exists_by_id(self, id: int) -> bool:
        """
        检查实体是否存在
        
        Args:
            id: 实体 ID
            
        Returns:
            是否存在
        """
        try:
            return self.db.query(self.model_class).filter(self.model_class.id == id).first() is not None
        except Exception as e:
            logger.error(f"检查{self.model_class.__name__}是否存在失败 (id={id}): {str(e)}")
            raise
    
    def count(self, filters: Optional[dict] = None) -> int:
        """
        统计实体数量
        
        Args:
            filters: 过滤条件字典
            
        Returns:
            实体数量
        """
        try:
            query = self.db.query(self.model_class)
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model_class, key) and value is not None:
                        query = query.filter(getattr(self.model_class, key) == value)
            return query.count()
        except Exception as e:
            logger.error(f"统计{self.model_class.__name__}数量失败: {str(e)}")
            raise
    
    def find_by_field(self, field_name: str, value: Any, options: Optional[list] = None) -> Optional[T]:
        """
        根据字段值查询单个实体
        
        Args:
            field_name: 字段名
            value: 字段值
            options: SQLAlchemy 查询选项
            
        Returns:
            查询到的实体，未找到返回 None
        """
        try:
            if not hasattr(self.model_class, field_name):
                raise ValueError(f"{self.model_class.__name__} 没有字段 {field_name}")
            
            query = self.db.query(self.model_class)
            if options:
                for option in options:
                    query = query.options(option)
            return query.filter(getattr(self.model_class, field_name) == value).first()
        except Exception as e:
            logger.error(f"查询{self.model_class.__name__}失败 ({field_name}={value}): {str(e)}")
            raise
    
    def exists_by_field(self, field_name: str, value: Any) -> bool:
        """
        检查字段值是否存在
        
        Args:
            field_name: 字段名
            value: 字段值
            
        Returns:
            是否存在
        """
        try:
            if not hasattr(self.model_class, field_name):
                raise ValueError(f"{self.model_class.__name__} 没有字段 {field_name}")
            
            return self.db.query(self.model_class).filter(
                getattr(self.model_class, field_name) == value
            ).first() is not None
        except Exception as e:
            logger.error(f"检查{self.model_class.__name__}是否存在失败 ({field_name}={value}): {str(e)}")
            raise
