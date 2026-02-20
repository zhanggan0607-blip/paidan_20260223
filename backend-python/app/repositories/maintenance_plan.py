from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from app.models.maintenance_plan import MaintenancePlan
import logging

logger = logging.getLogger(__name__)


class MaintenancePlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, id: int) -> Optional[MaintenancePlan]:
        try:
            return self.db.query(MaintenancePlan).filter(MaintenancePlan.id == id).first()
        except Exception as e:
            logger.error(f"查询维保计划失败 (id={id}): {str(e)}")
            raise

    def find_by_plan_id(self, plan_id: str) -> Optional[MaintenancePlan]:
        try:
            return self.db.query(MaintenancePlan).filter(MaintenancePlan.plan_id == plan_id).first()
        except Exception as e:
            logger.error(f"查询维保计划失败 (plan_id={plan_id}): {str(e)}")
            raise

    def exists_by_plan_id(self, plan_id: str) -> bool:
        try:
            return self.db.query(MaintenancePlan).filter(MaintenancePlan.plan_id == plan_id).first() is not None
        except Exception as e:
            logger.error(f"检查维保计划是否存在失败 (plan_id={plan_id}): {str(e)}")
            raise

    def find_all(
        self,
        page: int = 0,
        size: int = 10,
        plan_name: Optional[str] = None,
        project_id: Optional[str] = None,
        equipment_name: Optional[str] = None,
        plan_status: Optional[str] = None,
        status: Optional[str] = None,
        maintenance_personnel: Optional[str] = None,
        project_name: Optional[str] = None,
        client_name: Optional[str] = None,
        plan_type: Optional[str] = None,
        maintenance_personnel_filter: Optional[str] = None
    ) -> tuple[List[MaintenancePlan], int]:
        try:
            query = self.db.query(MaintenancePlan)

            if plan_name:
                query = query.filter(MaintenancePlan.plan_name.like(f"%{plan_name}%"))

            if project_id:
                query = query.filter(MaintenancePlan.project_id == project_id)

            if equipment_name:
                query = query.filter(MaintenancePlan.equipment_name.like(f"%{equipment_name}%"))

            if plan_status:
                query = query.filter(MaintenancePlan.plan_status == plan_status)

            if status:
                query = query.filter(MaintenancePlan.status == status)

            if maintenance_personnel:
                query = query.filter(MaintenancePlan.maintenance_personnel.like(f"%{maintenance_personnel}%"))

            if project_name:
                query = query.filter(MaintenancePlan.plan_name.like(f"%{project_name}%"))

            if client_name:
                query = query.filter(MaintenancePlan.responsible_department.like(f"%{client_name}%"))

            if plan_type:
                query = query.filter(MaintenancePlan.plan_type == plan_type)
            
            if maintenance_personnel_filter:
                query = query.filter(MaintenancePlan.maintenance_personnel == maintenance_personnel_filter)

            total = query.count()
            items = query.order_by(MaintenancePlan.created_at.desc()).offset(page * size).limit(size).all()

            return items, total
        except Exception as e:
            logger.error(f"查询维保计划列表失败: {str(e)}")
            raise

    def find_all_unpaginated(self) -> List[MaintenancePlan]:
        try:
            return self.db.query(MaintenancePlan).options(
                joinedload(MaintenancePlan.project)
            ).order_by(MaintenancePlan.created_at.desc()).all()
        except Exception as e:
            logger.error(f"查询所有维保计划失败: {str(e)}")
            raise

    def find_by_project_id_list(self, project_id: str) -> List[MaintenancePlan]:
        try:
            return self.db.query(MaintenancePlan).filter(
                MaintenancePlan.project_id == project_id
            ).order_by(MaintenancePlan.created_at.desc()).all()
        except Exception as e:
            logger.error(f"查询项目维保计划失败 (project_id={project_id}): {str(e)}")
            raise

    def find_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[MaintenancePlan]:
        try:
            return self.db.query(MaintenancePlan).filter(
                and_(
                    MaintenancePlan.execution_date >= start_date,
                    MaintenancePlan.execution_date <= end_date
                )
            ).order_by(MaintenancePlan.execution_date.asc()).all()
        except Exception as e:
            logger.error(f"查询日期范围内维保计划失败: {str(e)}")
            raise

    def find_upcoming_maintenance(self, days: int = 7) -> List[MaintenancePlan]:
        try:
            start_date = datetime.now()
            end_date = start_date + timedelta(days=days)
            return self.db.query(MaintenancePlan).filter(
                and_(
                    MaintenancePlan.execution_date >= start_date,
                    MaintenancePlan.execution_date <= end_date,
                    MaintenancePlan.status == '未进行'
                )
            ).order_by(MaintenancePlan.execution_date.asc()).all()
        except Exception as e:
            logger.error(f"查询即将到期的维保计划失败: {str(e)}")
            raise

    def create(self, maintenance_plan: MaintenancePlan) -> MaintenancePlan:
        try:
            logger.info(f"📥 [Repository] 准备插入数据: id={maintenance_plan.id}, plan_id={maintenance_plan.plan_id}")

            self.db.add(maintenance_plan)
            self.db.commit()
            self.db.refresh(maintenance_plan)
            logger.info(f"✅ [Repository] 数据库插入成功: id={maintenance_plan.id}, plan_id={maintenance_plan.plan_id}")
            return maintenance_plan
        except Exception as e:
            logger.error(f"❌ [Repository] 数据库插入失败: {str(e)}")
            self.db.rollback()
            logger.error(f"创建维保计划失败: {str(e)}")
            raise

    def update(self, maintenance_plan: MaintenancePlan) -> MaintenancePlan:
        try:
            self.db.commit()
            self.db.refresh(maintenance_plan)
            return maintenance_plan
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新维保计划失败: {str(e)}")
            raise

    def delete(self, maintenance_plan: MaintenancePlan) -> None:
        try:
            self.db.delete(maintenance_plan)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除维保计划失败: {str(e)}")
            raise

    def update_status(self, id: int, status: str) -> Optional[MaintenancePlan]:
        try:
            maintenance_plan = self.find_by_id(id)
            if maintenance_plan:
                maintenance_plan.status = status
                self.db.commit()
                self.db.refresh(maintenance_plan)
            return maintenance_plan
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新维保计划执行状态失败: {str(e)}")
            raise

    def update_completion_rate(self, id: int, rate: int) -> Optional[MaintenancePlan]:
        try:
            maintenance_plan = self.find_by_id(id)
            if maintenance_plan:
                maintenance_plan.completion_rate = rate
                self.db.commit()
                self.db.refresh(maintenance_plan)
            return maintenance_plan
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新维保计划完成率失败: {str(e)}")
            raise
