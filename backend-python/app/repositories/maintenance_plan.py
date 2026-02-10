from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.maintenance_plan import MaintenancePlan


class MaintenancePlanRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, id: int) -> Optional[MaintenancePlan]:
        return self.db.query(MaintenancePlan).filter(MaintenancePlan.id == id).first()
    
    def find_by_plan_id(self, plan_id: str) -> Optional[MaintenancePlan]:
        return self.db.query(MaintenancePlan).filter(MaintenancePlan.plan_id == plan_id).first()
    
    def exists_by_plan_id(self, plan_id: str) -> bool:
        return self.db.query(MaintenancePlan).filter(MaintenancePlan.plan_id == plan_id).first() is not None
    
    def find_all(
        self, 
        page: int = 0, 
        size: int = 10, 
        plan_name: Optional[str] = None, 
        project_id: Optional[str] = None,
        equipment_name: Optional[str] = None,
        plan_status: Optional[str] = None,
        execution_status: Optional[str] = None,
        responsible_person: Optional[str] = None,
        project_name: Optional[str] = None,
        client_name: Optional[str] = None
    ) -> tuple[List[MaintenancePlan], int]:
        query = self.db.query(MaintenancePlan)
        
        if plan_name:
            query = query.filter(MaintenancePlan.plan_name.like(f"%{plan_name}%"))
        
        if project_id:
            query = query.filter(MaintenancePlan.project_id == project_id)
        
        if equipment_name:
            query = query.filter(MaintenancePlan.equipment_name.like(f"%{equipment_name}%"))
        
        if plan_status:
            query = query.filter(MaintenancePlan.plan_status == plan_status)
        
        if execution_status:
            query = query.filter(MaintenancePlan.execution_status == execution_status)
        
        if responsible_person:
            query = query.filter(MaintenancePlan.responsible_person.like(f"%{responsible_person}%"))
        
        if project_name:
            query = query.filter(MaintenancePlan.plan_name.like(f"%{project_name}%"))
        
        if client_name:
            query = query.filter(MaintenancePlan.responsible_department.like(f"%{client_name}%"))
        
        total = query.count()
        items = query.order_by(MaintenancePlan.created_at.desc()).offset(page * size).limit(size).all()
        
        return items, total
    
    def find_all_unpaginated(self) -> List[MaintenancePlan]:
        return self.db.query(MaintenancePlan).order_by(MaintenancePlan.created_at.desc()).all()
    
    def find_by_project_id_list(self, project_id: str) -> List[MaintenancePlan]:
        return self.db.query(MaintenancePlan).filter(
            MaintenancePlan.project_id == project_id
        ).order_by(MaintenancePlan.created_at.desc()).all()
    
    def find_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[MaintenancePlan]:
        return self.db.query(MaintenancePlan).filter(
            and_(
                MaintenancePlan.execution_date >= start_date,
                MaintenancePlan.execution_date <= end_date
            )
        ).order_by(MaintenancePlan.execution_date.asc()).all()
    
    def find_upcoming_maintenance(self, days: int = 7) -> List[MaintenancePlan]:
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)
        return self.db.query(MaintenancePlan).filter(
            and_(
                MaintenancePlan.execution_date >= start_date,
                MaintenancePlan.execution_date <= end_date,
                MaintenancePlan.execution_status == '未开始'
            )
        ).order_by(MaintenancePlan.execution_date.asc()).all()
    
    def create(self, maintenance_plan: MaintenancePlan) -> MaintenancePlan:
        print(f"📥 [Repository] 准备插入数据: id={maintenance_plan.id}, plan_id={maintenance_plan.plan_id}")
        
        try:
            self.db.add(maintenance_plan)
            self.db.commit()
            self.db.refresh(maintenance_plan)
            print(f"✅ [Repository] 数据库插入成功: id={maintenance_plan.id}, plan_id={maintenance_plan.plan_id}")
            return maintenance_plan
        except Exception as e:
            print(f"❌ [Repository] 数据库插入失败: {str(e)}")
            self.db.rollback()
            raise e
    
    def update(self, maintenance_plan: MaintenancePlan) -> MaintenancePlan:
        self.db.commit()
        self.db.refresh(maintenance_plan)
        return maintenance_plan
    
    def delete(self, maintenance_plan: MaintenancePlan) -> None:
        self.db.delete(maintenance_plan)
        self.db.commit()
    
    def update_execution_status(self, id: int, status: str) -> Optional[MaintenancePlan]:
        maintenance_plan = self.find_by_id(id)
        if maintenance_plan:
            maintenance_plan.execution_status = status
            self.db.commit()
            self.db.refresh(maintenance_plan)
        return maintenance_plan
    
    def update_completion_rate(self, id: int, rate: int) -> Optional[MaintenancePlan]:
        maintenance_plan = self.find_by_id(id)
        if maintenance_plan:
            maintenance_plan.completion_rate = rate
            self.db.commit()
            self.db.refresh(maintenance_plan)
        return maintenance_plan
