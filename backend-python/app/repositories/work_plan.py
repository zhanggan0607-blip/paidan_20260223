from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.work_plan import WorkPlan
import logging

logger = logging.getLogger(__name__)


class WorkPlanRepository:
    def __init__(self, db: Session):
        self._db = db
    
    @property
    def db(self):
        return self._db

    def find_all(
        self,
        page: int = 0,
        size: int = 10,
        plan_type: Optional[str] = None,
        project_name: Optional[str] = None,
        client_name: Optional[str] = None,
        status: Optional[str] = None
    ) -> tuple[List[WorkPlan], int]:
        try:
            query = self.db.query(WorkPlan)

            if plan_type:
                query = query.filter(WorkPlan.plan_type == plan_type)

            if project_name:
                query = query.filter(WorkPlan.project_name.like(f'%{project_name}%'))

            if client_name:
                query = query.filter(WorkPlan.client_name.like(f'%{client_name}%'))

            if status:
                query = query.filter(WorkPlan.status == status)

            total = query.count()
            items = query.order_by(WorkPlan.created_at.desc()).offset(page * size).limit(size).all()

            return items, total
        except Exception as e:
            logger.error(f"查询工作计划列表失败: {str(e)}")
            raise

    def find_by_id(self, id: int) -> Optional[WorkPlan]:
        try:
            return self.db.query(WorkPlan).filter(WorkPlan.id == id).first()
        except Exception as e:
            logger.error(f"查询工作计划失败 (id={id}): {str(e)}")
            raise

    def find_by_plan_id(self, plan_id: str) -> Optional[WorkPlan]:
        try:
            return self.db.query(WorkPlan).filter(WorkPlan.plan_id == plan_id).first()
        except Exception as e:
            logger.error(f"查询工作计划失败 (plan_id={plan_id}): {str(e)}")
            raise

    def exists_by_plan_id(self, plan_id: str) -> bool:
        try:
            return self.db.query(WorkPlan).filter(WorkPlan.plan_id == plan_id).first() is not None
        except Exception as e:
            logger.error(f"检查工作计划是否存在失败 (plan_id={plan_id}): {str(e)}")
            raise

    def create(self, work_plan: WorkPlan) -> WorkPlan:
        try:
            self.db.add(work_plan)
            self.db.commit()
            self.db.refresh(work_plan)
            return work_plan
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建工作计划失败: {str(e)}")
            raise

    def update(self, work_plan: WorkPlan) -> WorkPlan:
        try:
            self.db.commit()
            self.db.refresh(work_plan)
            return work_plan
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新工作计划失败: {str(e)}")
            raise

    def delete(self, work_plan: WorkPlan) -> None:
        try:
            self.db.delete(work_plan)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除工作计划失败: {str(e)}")
            raise

    def find_all_unpaginated(self, plan_type: Optional[str] = None) -> List[WorkPlan]:
        try:
            query = self.db.query(WorkPlan)
            if plan_type:
                query = query.filter(WorkPlan.plan_type == plan_type)
            return query.order_by(WorkPlan.created_at.desc()).all()
        except Exception as e:
            logger.error(f"查询所有工作计划失败: {str(e)}")
            raise
