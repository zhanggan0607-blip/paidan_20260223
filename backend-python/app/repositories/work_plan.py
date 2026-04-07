import logging

from sqlalchemy.orm import Session, joinedload

from app.models.work_plan import WorkPlan

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
        plan_type: str | None = None,
        project_name: str | None = None,
        client_name: str | None = None,
        status: str | None = None,
        maintenance_personnel: str | None = None
    ) -> tuple[list[WorkPlan], int]:
        try:
            query = self.db.query(WorkPlan).options(joinedload(WorkPlan.project)).filter(
                WorkPlan.is_deleted == False
            )

            if plan_type:
                query = query.filter(WorkPlan.plan_type == plan_type)

            if project_name:
                query = query.filter(WorkPlan.project_name.like(f'%{project_name}%'))

            if client_name:
                query = query.filter(WorkPlan.client_name.like(f'%{client_name}%'))

            if status:
                query = query.filter(WorkPlan.status == status)

            if maintenance_personnel:
                query = query.filter(WorkPlan.maintenance_personnel == maintenance_personnel)

            total = query.count()
            items = query.order_by(WorkPlan.created_at.desc()).offset(page * size).limit(size).all()

            return items, total
        except Exception as e:
            logger.error(f"查询工作计划列表失败: {str(e)}")
            raise

    def find_by_id(self, id: int) -> WorkPlan | None:
        try:
            return self.db.query(WorkPlan).options(joinedload(WorkPlan.project)).filter(
                WorkPlan.id == id,
                WorkPlan.is_deleted == False
            ).first()
        except Exception as e:
            logger.error(f"查询工作计划失败 (id={id}): {str(e)}")
            raise

    def find_by_plan_id(self, plan_id: str) -> WorkPlan | None:
        try:
            return self.db.query(WorkPlan).options(joinedload(WorkPlan.project)).filter(
                WorkPlan.plan_id == plan_id,
                WorkPlan.is_deleted == False
            ).first()
        except Exception as e:
            logger.error(f"查询工作计划失败 (plan_id={plan_id}): {str(e)}")
            raise

    def exists_by_plan_id(self, plan_id: str) -> bool:
        try:
            return self.db.query(WorkPlan).filter(
                WorkPlan.plan_id == plan_id,
                WorkPlan.is_deleted == False
            ).first() is not None
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

    def soft_delete(self, work_plan: WorkPlan, user_id: int = None) -> None:
        """
        软删除工作计划

        Args:
            work_plan: 要删除的工作计划对象
            user_id: 执行删除的用户ID
        """
        try:
            work_plan.soft_delete(user_id)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"软删除工作计划失败: {str(e)}")
            raise

    def delete(self, work_plan: WorkPlan) -> None:
        """
        物理删除（已弃用，请使用soft_delete）
        """
        try:
            self.db.delete(work_plan)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除工作计划失败: {str(e)}")
            raise

    def find_all_unpaginated(self, plan_type: str | None = None) -> list[WorkPlan]:
        try:
            query = self.db.query(WorkPlan).options(joinedload(WorkPlan.project)).filter(
                WorkPlan.is_deleted == False
            )
            if plan_type:
                query = query.filter(WorkPlan.plan_type == plan_type)
            return query.order_by(WorkPlan.created_at.desc()).all()
        except Exception as e:
            logger.error(f"查询所有工作计划失败: {str(e)}")
            raise
