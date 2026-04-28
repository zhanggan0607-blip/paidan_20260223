import logging

from sqlalchemy.orm import Session

from app.exceptions import NotFoundException, ValidationException
from app.models.customer_contact import CustomerContact
from app.repositories.customer import CustomerRepository
from app.repositories.customer_contact import CustomerContactRepository
from app.schemas.customer import (
    CustomerCreate,
    CustomerListResponse,
    CustomerResponse,
    CustomerUpdate,
)
from app.schemas.customer_contact import CustomerContactResponse

logger = logging.getLogger(__name__)


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
        self.contact_repository = CustomerContactRepository(db)

    def get_list(self, page: int = 0, size: int = 10, name: str | None = None, contact_person: str | None = None, client_names: list[str] | None = None) -> CustomerListResponse:
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

        content = []
        for item in items:
            contacts = self.contact_repository.get_by_customer_id(item.id)
            contact_persons = [c.contact_person for c in contacts if c.contact_person]
            phones = [c.phone for c in contacts if c.phone]
            positions = [c.contact_position for c in contacts if c.contact_position]

            first_contact = contacts[0] if contacts else None

            customer_response = CustomerResponse(
                id=item.id,
                name=item.name,
                address=item.address,
                contact_person=first_contact.contact_person if first_contact else None,
                phone=first_contact.phone if first_contact else None,
                contact_position=first_contact.contact_position if first_contact else None,
                remarks=item.remarks,
                contacts=[CustomerContactResponse.model_validate(c) for c in contacts],
                created_at=item.created_at,
                updated_at=item.updated_at
            )
            content.append(customer_response)

        return CustomerListResponse(
            content=content,
            totalElements=total,
            totalPages=(total + size - 1) // size if size > 0 else 0,
            size=size,
            number=page
        )

    def get_user_client_names(self, user_name: str) -> list[str]:
        """
        获取用户关联的客户名称列表（通过项目和工单关联）
        @param user_name: 用户名
        @return: 客户名称列表
        """
        from app.models.periodic_inspection import PeriodicInspection
        from app.models.project_info import ProjectInfo
        from app.models.spot_work import SpotWork
        from app.models.temporary_repair import TemporaryRepair
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

    def get_by_id(self, customer_id: int) -> CustomerResponse | None:
        """
        根据ID获取客户信息
        @param customer_id: 客户ID
        @return: 客户响应对象，不存在则返回None
        """
        customer = self.repository.get_by_id(customer_id)
        if customer:
            contacts = self.contact_repository.get_by_customer_id(customer_id)
            first_contact = contacts[0] if contacts else None

            return CustomerResponse(
                id=customer.id,
                name=customer.name,
                address=customer.address,
                contact_person=first_contact.contact_person if first_contact else None,
                phone=first_contact.phone if first_contact else None,
                contact_position=first_contact.contact_position if first_contact else None,
                remarks=customer.remarks,
                contacts=[CustomerContactResponse.model_validate(c) for c in contacts],
                created_at=customer.created_at,
                updated_at=customer.updated_at
            )
        return None

    def create(self, customer: CustomerCreate) -> CustomerResponse:
        """
        创建新客户
        @param customer: 客户创建数据传输对象
        @return: 创建成功的客户响应对象
        @raises ValidationException: 客户名称已存在时抛出异常
        """
        if self.repository.exists_by_name(customer.name):
            raise ValidationException(f"客户单位「{customer.name}」已存在，不能重复添加")

        db_customer = self.repository.create(customer)

        contacts = []
        if customer.contacts:
            db_contacts = self.contact_repository.bulk_create(db_customer.id, customer.contacts)
            contacts = [CustomerContactResponse.model_validate(c) for c in db_contacts]

        self.db.commit()

        first_contact = contacts[0] if contacts else None
        return CustomerResponse(
            id=db_customer.id,
            name=db_customer.name,
            address=db_customer.address,
            contact_person=first_contact.contact_person if first_contact else None,
            phone=first_contact.phone if first_contact else None,
            contact_position=first_contact.contact_position if first_contact else None,
            remarks=db_customer.remarks,
            contacts=contacts,
            created_at=db_customer.created_at,
            updated_at=db_customer.updated_at
        )

    def update(self, customer_id: int, customer: CustomerUpdate) -> CustomerResponse | None:
        """
        更新客户信息
        @param customer_id: 客户ID
        @param customer: 客户更新数据传输对象
        @return: 更新后的客户响应对象，不存在则返回None
        @raises ValidationException: 客户名称已存在时抛出异常
        """
        existing_customer = self.repository.get_by_id(customer_id)
        if not existing_customer:
            return None

        if customer.name and customer.name != existing_customer.name:
            if self.repository.exists_by_name(customer.name, exclude_id=customer_id):
                raise ValidationException(f"客户单位「{customer.name}」已存在，不能重复添加")

        db_customer = self.repository.update(customer_id, customer)
        if not db_customer:
            return None

        if customer.contacts is not None:
            self.contact_repository.delete_by_customer_id(customer_id)
            contacts = []
            if customer.contacts:
                db_contacts = self.contact_repository.bulk_create(customer_id, customer.contacts)
                contacts = [CustomerContactResponse.model_validate(c) for c in db_contacts]
        else:
            db_contacts = self.contact_repository.get_by_customer_id(customer_id)
            contacts = [CustomerContactResponse.model_validate(c) for c in db_contacts]

        self.db.commit()

        first_contact = contacts[0] if contacts else None
        return CustomerResponse(
            id=db_customer.id,
            name=db_customer.name,
            address=db_customer.address,
            contact_person=first_contact.contact_person if first_contact else None,
            phone=first_contact.phone if first_contact else None,
            contact_position=first_contact.contact_position if first_contact else None,
            remarks=db_customer.remarks,
            contacts=contacts,
            created_at=db_customer.created_at,
            updated_at=db_customer.updated_at
        )

    def delete(self, customer_id: int) -> dict:
        """
        删除客户
        删除前会检查是否有关联的项目，有则拒绝删除
        @param customer_id: 客户ID
        @return: 删除结果信息
        @raises NotFoundException: 客户不存在时抛出异常
        @raises ValidationException: 有关联项目时抛出异常
        """
        from app.models.project_info import ProjectInfo

        customer = self.repository.get_by_id(customer_id)
        if not customer:
            raise NotFoundException("客户不存在")

        customer_name = customer.name

        projects = self.db.query(ProjectInfo).filter(
            ProjectInfo.client_name == customer_name
        ).all()
        project_count = len(projects)

        if project_count > 0:
            raise ValidationException(f"该客户下有 {project_count} 个项目，无法删除。请先在项目信息管理中删除相关项目。")

        self.contact_repository.delete_by_customer_id(customer_id)
        self.repository.delete(customer_id)
        self.db.commit()

        return {
            'customer_name': customer_name,
            'deleted_related': {}
        }

    def get_contacts_by_customer_name(self, customer_name: str) -> list[CustomerContactResponse]:
        """
        根据客户单位名称获取联系人列表
        @param customer_name: 客户单位名称
        @return: 联系人列表
        """
        from app.models.customer import Customer as CustomerModel

        customer = self.db.query(CustomerModel).filter(CustomerModel.name == customer_name).first()
        if not customer:
            return []

        contacts = self.contact_repository.get_by_customer_id(customer.id)
        return [CustomerContactResponse.model_validate(c) for c in contacts]
