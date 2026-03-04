"""
定期巡检Repository
提供定期巡检数据访问方法
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.periodic_inspection import PeriodicInspection
from app.repositories.base import BaseRepository
import logging

logger = logging.getLogger(__name__)


class PeriodicInspectionRepository(BaseRepository[PeriodicInspection]):
    """
    定期巡检Repository
    继承BaseRepository，复用通用CRUD方法
    """
    
    def __init__(self, db: Session):
        super().__init__(db, PeriodicInspection)

    def find_by_id(self, id: int) -> Optional[PeriodicInspection]:
        """
        根据ID查询定期巡检
        
        Args:
            id: 巡检单ID
            
        Returns:
            巡检单对象，未找到返回None
        """
        try:
            return self.db.query(PeriodicInspection).options(
                joinedload(PeriodicInspection.project)
            ).filter(
                PeriodicInspection.id == id,
                PeriodicInspection.is_deleted == False
            ).first()
        except Exception as e:
            logger.error(f"查询定期巡检失败 (id={id}): {str(e)}")
            raise

    def find_by_inspection_id(self, inspection_id: str) -> Optional[PeriodicInspection]:
        """
        根据巡检单编号查询
        
        Args:
            inspection_id: 巡检单编号
            
        Returns:
            巡检单对象，未找到返回None
        """
        try:
            return self.db.query(PeriodicInspection).filter(
                PeriodicInspection.inspection_id == inspection_id,
                PeriodicInspection.is_deleted == False
            ).first()
        except Exception as e:
            logger.error(f"查询定期巡检失败 (inspection_id={inspection_id}): {str(e)}")
            raise

    def exists_by_inspection_id(self, inspection_id: str) -> bool:
        """
        检查巡检单编号是否存在
        
        Args:
            inspection_id: 巡检单编号
            
        Returns:
            是否存在
        """
        try:
            return self.db.query(PeriodicInspection).filter(
                PeriodicInspection.inspection_id == inspection_id,
                PeriodicInspection.is_deleted == False
            ).first() is not None
        except Exception as e:
            logger.error(f"检查定期巡检是否存在失败 (inspection_id={inspection_id}): {str(e)}")
            raise

    def find_all(
        self,
        page: int = 0,
        size: int = 10,
        project_name: Optional[str] = None,
        client_name: Optional[str] = None,
        inspection_id: Optional[str] = None,
        status: Optional[str] = None,
        maintenance_personnel: Optional[str] = None
    ) -> tuple[List[PeriodicInspection], int]:
        """
        分页查询定期巡检列表
        
        Args:
            page: 页码
            size: 每页数量
            project_name: 项目名称（模糊查询）
            client_name: 客户名称（模糊查询）
            inspection_id: 巡检单编号（模糊查询）
            status: 状态
            maintenance_personnel: 运维人员
            
        Returns:
            (巡检单列表, 总数)
        """
        try:
            query = self.db.query(PeriodicInspection).options(
                joinedload(PeriodicInspection.project)
            ).filter(PeriodicInspection.is_deleted == False)

            if project_name:
                query = query.filter(PeriodicInspection.project_name.like(f"%{project_name}%"))

            if client_name:
                query = query.filter(PeriodicInspection.client_name.like(f"%{client_name}%"))

            if inspection_id:
                query = query.filter(PeriodicInspection.inspection_id.like(f"%{inspection_id}%"))

            if status:
                query = query.filter(PeriodicInspection.status == status)
            
            if maintenance_personnel:
                query = query.filter(PeriodicInspection.maintenance_personnel == maintenance_personnel)

            total = query.count()
            items = query.order_by(PeriodicInspection.updated_at.desc().nullslast(), PeriodicInspection.created_at.desc()).offset(page * size).limit(size).all()

            return items, total
        except Exception as e:
            logger.error(f"查询定期巡检列表失败: {str(e)}")
            raise

    def find_all_unpaginated(self) -> List[PeriodicInspection]:
        """
        查询所有定期巡检（不分页）
        
        Returns:
            巡检单列表
        """
        try:
            return self.db.query(PeriodicInspection).options(
                joinedload(PeriodicInspection.project)
            ).filter(
                PeriodicInspection.is_deleted == False
            ).order_by(PeriodicInspection.updated_at.desc().nullslast(), PeriodicInspection.created_at.desc()).all()
        except Exception as e:
            logger.error(f"查询所有定期巡检失败: {str(e)}")
            raise

    def soft_delete(self, inspection: PeriodicInspection, user_id: int = None) -> None:
        """
        软删除定期巡检单
        
        Args:
            inspection: 要删除的巡检单对象
            user_id: 执行删除的用户ID
        """
        try:
            inspection.soft_delete(user_id)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"软删除定期巡检失败: {str(e)}")
            raise
