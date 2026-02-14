from sqlalchemy.orm import Session
from app.repositories.customer import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse, CustomerListResponse
from typing import Optional
import logging
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class CustomerService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = CustomerRepository(db)

    def get_list(self, page: int = 0, size: int = 10, name: Optional[str] = None, contact_person: Optional[str] = None) -> CustomerListResponse:
        skip = page * size
        items, total = self.repository.get_all(skip=skip, limit=size, name=name, contact_person=contact_person)
        
        return CustomerListResponse(
            content=[CustomerResponse.model_validate(item) for item in items],
            totalElements=total,
            totalPages=(total + size - 1) // size if size > 0 else 0,
            size=size,
            number=page
        )

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

    def delete(self, customer_id: int, cascade: bool = False) -> dict:
        from app.models.project_info import ProjectInfo
        from app.models.work_plan import WorkPlan
        from app.models.periodic_inspection import PeriodicInspection
        from app.models.temporary_repair import TemporaryRepair
        from app.models.spot_work import SpotWork
        from app.models.maintenance_plan import MaintenancePlan
        
        customer = self.repository.get_by_id(customer_id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="客户不存在")
        
        customer_name = customer.name
        
        projects = self.db.query(ProjectInfo).filter(ProjectInfo.client_name == customer_name).all()
        project_count = len(projects)
        
        if project_count > 0 and not cascade:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该客户下有 {project_count} 个项目，请确认是否级联删除"
            )
        
        deleted_counts = {}
        
        if cascade and project_count > 0:
            for project in projects:
                project_id = project.project_id
                
                work_plan_count = self.db.query(WorkPlan).filter(WorkPlan.project_id == project_id).count()
                periodic_count = self.db.query(PeriodicInspection).filter(PeriodicInspection.project_id == project_id).count()
                repair_count = self.db.query(TemporaryRepair).filter(TemporaryRepair.project_id == project_id).count()
                spot_count = self.db.query(SpotWork).filter(SpotWork.project_id == project_id).count()
                maintenance_count = self.db.query(MaintenancePlan).filter(MaintenancePlan.project_id == project_id).count()
                
                if work_plan_count > 0:
                    self.db.query(WorkPlan).filter(WorkPlan.project_id == project_id).delete(synchronize_session=False)
                    deleted_counts['work_plan'] = deleted_counts.get('work_plan', 0) + work_plan_count
                
                if periodic_count > 0:
                    self.db.query(PeriodicInspection).filter(PeriodicInspection.project_id == project_id).delete(synchronize_session=False)
                    deleted_counts['periodic_inspection'] = deleted_counts.get('periodic_inspection', 0) + periodic_count
                
                if repair_count > 0:
                    self.db.query(TemporaryRepair).filter(TemporaryRepair.project_id == project_id).delete(synchronize_session=False)
                    deleted_counts['temporary_repair'] = deleted_counts.get('temporary_repair', 0) + repair_count
                
                if spot_count > 0:
                    self.db.query(SpotWork).filter(SpotWork.project_id == project_id).delete(synchronize_session=False)
                    deleted_counts['spot_work'] = deleted_counts.get('spot_work', 0) + spot_count
                
                if maintenance_count > 0:
                    self.db.query(MaintenancePlan).filter(MaintenancePlan.project_id == project_id).delete(synchronize_session=False)
                    deleted_counts['maintenance_plan'] = deleted_counts.get('maintenance_plan', 0) + maintenance_count
            
            self.db.query(ProjectInfo).filter(ProjectInfo.client_name == customer_name).delete(synchronize_session=False)
            deleted_counts['project'] = project_count
            
            self.db.commit()
        
        self.repository.delete(customer_id)
        
        return {
            'customer_name': customer_name,
            'deleted_related': deleted_counts
        }
