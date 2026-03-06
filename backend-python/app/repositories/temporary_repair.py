"""
临时维修Repository
提供临时维修数据访问方法
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.temporary_repair import TemporaryRepair
from app.repositories.base import BaseRepository
import logging

logger = logging.getLogger(__name__)


class TemporaryRepairRepository(BaseRepository[TemporaryRepair]):
    """
    临时维修Repository
    继承BaseRepository，复用通用CRUD方法
    """
    
    def __init__(self, db: Session):
        super().__init__(db, TemporaryRepair)

    def find_all(
        self,
        page: int = 0,
        size: int = 10,
        project_name: Optional[str] = None,
        repair_id: Optional[str] = None,
        status: Optional[str] = None,
        maintenance_personnel: Optional[str] = None,
        client_name: Optional[str] = None
    ) -> tuple[List[TemporaryRepair], int]:
        """
        分页查询临时维修列表
        
        Args:
            page: 页码
            size: 每页数量
            project_name: 项目名称（模糊查询）
            repair_id: 维修单编号（模糊查询）
            status: 状态
            maintenance_personnel: 运维人员
            client_name: 客户名称（模糊查询）
            
        Returns:
            (维修单列表, 总数)
        """
        try:
            query = self.db.query(TemporaryRepair).options(
                joinedload(TemporaryRepair.project)
            ).filter(TemporaryRepair.is_deleted == False)

            if project_name:
                query = query.filter(TemporaryRepair.project_name.like(f'%{project_name}%'))

            if repair_id:
                query = query.filter(TemporaryRepair.repair_id.like(f'%{repair_id}%'))

            if status:
                query = query.filter(TemporaryRepair.status == status)
            
            if maintenance_personnel:
                query = query.filter(TemporaryRepair.maintenance_personnel == maintenance_personnel)
            
            if client_name:
                query = query.filter(TemporaryRepair.client_name.like(f'%{client_name}%'))

            total = query.count()
            items = query.order_by(TemporaryRepair.created_at.desc()).offset(page * size).limit(size).all()

            return items, total
        except Exception as e:
            logger.error(f"查询临时维修列表失败: {str(e)}")
            raise

    def find_by_id(self, id: int) -> Optional[TemporaryRepair]:
        """
        根据ID查询临时维修
        
        Args:
            id: 维修单ID
            
        Returns:
            维修单对象，未找到返回None
        """
        try:
            return self.db.query(TemporaryRepair).options(
                joinedload(TemporaryRepair.project)
            ).filter(
                TemporaryRepair.id == id,
                TemporaryRepair.is_deleted == False
            ).first()
        except Exception as e:
            logger.error(f"查询临时维修失败 (id={id}): {str(e)}")
            raise

    def find_by_repair_id(self, repair_id: str) -> Optional[TemporaryRepair]:
        """
        根据维修单编号查询
        
        Args:
            repair_id: 维修单编号
            
        Returns:
            维修单对象，未找到返回None
        """
        try:
            return self.db.query(TemporaryRepair).options(
                joinedload(TemporaryRepair.project)
            ).filter(
                TemporaryRepair.repair_id == repair_id,
                TemporaryRepair.is_deleted == False
            ).first()
        except Exception as e:
            logger.error(f"查询临时维修失败 (repair_id={repair_id}): {str(e)}")
            raise

    def exists_by_repair_id(self, repair_id: str, include_deleted: bool = False) -> bool:
        """
        检查维修单编号是否存在
        
        Args:
            repair_id: 维修单编号
            include_deleted: 是否包含已删除的记录
            
        Returns:
            是否存在
        """
        try:
            query = self.db.query(TemporaryRepair).filter(
                TemporaryRepair.repair_id == repair_id
            )
            if not include_deleted:
                query = query.filter(TemporaryRepair.is_deleted == False)
            return query.first() is not None
        except Exception as e:
            logger.error(f"检查临时维修是否存在失败 (repair_id={repair_id}): {str(e)}")
            raise

    def soft_delete(self, repair: TemporaryRepair, user_id: int = None) -> None:
        """
        软删除临时维修单
        
        Args:
            repair: 要删除的维修单对象
            user_id: 执行删除的用户ID
        """
        try:
            repair.soft_delete(user_id)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"软删除临时维修失败: {str(e)}")
            raise

    def find_all_unpaginated(self) -> List[TemporaryRepair]:
        """
        查询所有临时维修（不分页）
        
        Returns:
            维修单列表
        """
        try:
            return self.db.query(TemporaryRepair).options(
                joinedload(TemporaryRepair.project)
            ).filter(
                TemporaryRepair.is_deleted == False
            ).all()
        except Exception as e:
            logger.error(f"查询所有临时维修失败: {str(e)}")
            raise
