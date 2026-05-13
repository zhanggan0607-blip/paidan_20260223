from app.utils.logging_config import get_logger

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate

logger = get_logger(__name__)


class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 10, name: str | None = None, contact_person: str | None = None, client_names: list[str] | None = None) -> tuple[list[Customer], int]:
        try:
            query = self.db.query(Customer)

            if name:
                query = query.filter(Customer.name.ilike(f"%{name}%"))
            if client_names:
                query = query.filter(Customer.name.in_(client_names))

            total = query.count()
            items = query.order_by(Customer.created_at.desc(), Customer.id.desc()).offset(skip).limit(limit).all()

            return items, total
        except Exception as e:
            logger.error(f"查询客户列表失败: {str(e)}")
            raise

    def get_by_id(self, customer_id: int) -> Customer | None:
        try:
            return self.db.query(Customer).filter(Customer.id == customer_id).first()
        except Exception as e:
            logger.error(f"查询客户失败 (id={customer_id}): {str(e)}")
            raise

    def get_by_name(self, name: str) -> Customer | None:
        """
        根据客户名称查询客户
        @param name: 客户名称
        @return: 客户对象，不存在则返回None
        """
        try:
            return self.db.query(Customer).filter(Customer.name == name).first()
        except Exception as e:
            logger.error(f"查询客户失败 (name={name}): {str(e)}")
            raise

    def exists_by_name(self, name: str, exclude_id: int | None = None) -> bool:
        """
        检查客户名称是否已存在
        @param name: 客户名称
        @param exclude_id: 排除的客户ID（用于更新时排除自身）
        @return: 是否存在
        """
        try:
            query = self.db.query(Customer).filter(Customer.name == name)
            if exclude_id:
                query = query.filter(Customer.id != exclude_id)
            return query.first() is not None
        except Exception as e:
            logger.error(f"检查客户名称是否存在失败 (name={name}): {str(e)}")
            raise

    def create(self, customer: CustomerCreate) -> Customer:
        try:
            db_customer = Customer(
                name=customer.name,
                address=customer.address,
                remarks=customer.remarks
            )
            self.db.add(db_customer)
            self.db.flush()
            return db_customer
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建客户失败: {str(e)}")
            raise

    def update(self, customer_id: int, customer: CustomerUpdate) -> Customer | None:
        try:
            db_customer = self.get_by_id(customer_id)
            if not db_customer:
                return None

            update_data = customer.model_dump(exclude_unset=True)
            if 'contacts' in update_data:
                del update_data['contacts']

            for key, value in update_data.items():
                setattr(db_customer, key, value)

            self.db.flush()
            return db_customer
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新客户失败 (id={customer_id}): {str(e)}")
            raise

    def delete(self, customer_id: int) -> bool:
        try:
            db_customer = self.get_by_id(customer_id)
            if not db_customer:
                return False

            self.db.delete(db_customer)
            self.db.flush()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除客户失败 (id={customer_id}): {str(e)}")
            raise
