from sqlalchemy.orm import Session
from app.repositories.customer import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse, CustomerListResponse
from typing import Optional, List
import logging
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


# TODO: 客户服务 - 考虑加入客户等级/信用度管理
# FIXME: get_user_client_names 方法查询效率低，应该优化SQL
# TODO: 客户信息变更时应该通知相关人员
class CustomerService:
    """
    客户管理服务类
    提供客户的增删改查等业务逻辑处理
    """
    
    def __init__(self, db: Session):
        """
        初始化客户服务
        @param db: 数据库会话对象
        """
        self.db = db
        self.repository = CustomerRepository(db)

    def get_list(self, page: int = 0, size: int = 10, name: Optional[str] = None, contact_person: Optional[str] = None, client_names: Optional[List[str]] = None) -> CustomerListResponse:
        """
        分页获取客户列表
        @param page: 页码，从0开始
        @param size: 每页大小
        @param name: 客户名称模糊查询条件
        @param contact_person: 联系人模糊查询条件
        @param client_names: 客户名称列表，用于精确筛选
        @return: 分页响应对象
        """
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
        """
        获取用户关联的客户名称列表（通过项目和工单关联）
        @param user_name: 用户名
        @return: 客户名称列表
        """
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
        """
        根据ID获取客户信息
        @param customer_id: 客户ID
        @return: 客户响应对象，不存在则返回None
        """
        customer = self.repository.get_by_id(customer_id)
        if customer:
            return CustomerResponse.model_validate(customer)
        return None

    def create(self, customer: CustomerCreate) -> CustomerResponse:
        """
        创建新客户
        @param customer: 客户创建数据传输对象
        @return: 创建成功的客户响应对象
        """
        db_customer = self.repository.create(customer)
        return CustomerResponse.model_validate(db_customer)

    def update(self, customer_id: int, customer: CustomerUpdate) -> Optional[CustomerResponse]:
        """
        更新客户信息
        @param customer_id: 客户ID
        @param customer: 客户更新数据传输对象
        @return: 更新后的客户响应对象，不存在则返回None
        """
        db_customer = self.repository.update(customer_id, customer)
        if db_customer:
            return CustomerResponse.model_validate(db_customer)
        return None

    def delete(self, customer_id: int) -> dict:
        """
        删除客户
        删除前会检查是否有关联的项目，有则拒绝删除
        @param customer_id: 客户ID
        @return: 删除结果信息
        @raises HTTPException: 客户不存在或有关联项目时抛出异常
        """
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
