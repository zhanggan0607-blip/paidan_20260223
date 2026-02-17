from sqlalchemy.orm import Session
from app.repositories.customer import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse, CustomerListResponse
from typing import Optional, List
import logging
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class CustomerService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = CustomerRepository(db)

    def get_list(self, page: int = 0, size: int = 10, name: Optional[str] = None, contact_person: Optional[str] = None, client_names: Optional[List[str]] = None) -> CustomerListResponse:
        skip = page * size
        items, total = self.repository.get_all(skip=skip, limit=size, name=name, contact_person=contact_person, client_names=client_names)
        
        return CustomerListResponse(
            content=[CustomerResponse.model_validate(item) for item in items],
            totalElements=total,
            totalPages=(total + size - 1) // size if size > 0 else 0,
            size=size,
            number=page
        )
    
    def get_user_client_names(self, user_name: str) -> List[str]:
        """获取用户关联的客户名称列表（通过项目和工单关联）"""
        from app.models.project_info import ProjectInfo
        from app.models.periodic_inspection import PeriodicInspection
        from app.models.temporary_repair import TemporaryRepair
        from app.models.spot_work import SpotWork
        from app.models.work_plan import WorkPlan
        
        project_ids = set()
        
        periodic = self.db.query(PeriodicInspection.project_id).filter(
            PeriodicInspection.maintenance_personnel == user_name
        ).all()
        project_ids.update([p[0] for p in periodic if p[0]])
        
        repair = self.db.query(TemporaryRepair.project_id).filter(
            TemporaryRepair.maintenance_personnel == user_name
        ).all()
        project_ids.update([p[0] for p in repair if p[0]])
        
        spot = self.db.query(SpotWork.project_id).filter(
            SpotWork.maintenance_personnel == user_name
        ).all()
        project_ids.update([p[0] for p in spot if p[0]])
        
        work_plan = self.db.query(WorkPlan.project_id).filter(
            WorkPlan.maintenance_personnel == user_name
        ).all()
        project_ids.update([p[0] for p in work_plan if p[0]])
        
        if not project_ids:
            return []
        
        clients = self.db.query(ProjectInfo.client_name).filter(
            ProjectInfo.project_id.in_(list(project_ids))
        ).distinct().all()
        
        return [c[0] for c in clients if c[0]]

    def get_by_id(self, customer_id: int) -> Optional[CustomerResponse]:
        customer = self.repository.get_by_id(customer_id)
        if customer:
            return CustomerResponse.model_validate(customer)
        return None

    def create(self, customer: CustomerCreate) -> CustomerResponse:
        db_customer = self.repository.create(customer)
        return CustomerResponse.model_validate(db_customer)

    def update(self, customer_id: int, customer: CustomerUpdate) -> Optional[CustomerResponse]:
        db_customer = self.repository.update(customer_id, customer)
        if db_customer:
            return CustomerResponse.model_validate(db_customer)
        return None

    def delete(self, customer_id: int) -> dict:
        from app.models.work_plan import WorkPlan
        from app.models.periodic_inspection import PeriodicInspection
        from app.models.temporary_repair import TemporaryRepair
        from app.models.spot_work import SpotWork
        from app.models.maintenance_plan import MaintenancePlan
        from app.models.project_info import ProjectInfo
        
        customer = self.repository.get_by_id(customer_id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="客户不存在")
        
        customer_name = customer.name
        
        projects = self.db.query(ProjectInfo).filter(ProjectInfo.client_name == customer_name).all()
        project_count = len(projects)
        
        if project_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该客户下有 {project_count} 个项目，无法删除。请先在项目信息管理中删除相关项目。"
            )
        
        self.repository.delete(customer_id)
        
        return {
            'customer_name': customer_name,
            'deleted_related': {}
        }
