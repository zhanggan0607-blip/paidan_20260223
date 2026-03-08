import logging

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate

logger = logging.getLogger(__name__)

class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 10, name: str | None = None, contact_person: str | None = None, client_names: list[str] | None = None) -> tuple[list[Customer], int]:
        try:
            query = self.db.query(Customer)

            if name:
                query = query.filter(Customer.name.ilike(f"%{name}%"))
            if contact_person:
                query = query.filter(Customer.contact_person.ilike(f"%{contact_person}%"))
            if client_names:
                query = query.filter(Customer.name.in_(client_names))

            total = query.count()
            items = query.order_by(Customer.created_at.desc()).offset(skip).limit(limit).all()

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

    def create(self, customer: CustomerCreate) -> Customer:
        try:
            db_customer = Customer(
                name=customer.name,
                address=customer.address,
                contact_person=customer.contact_person,
                phone=customer.phone,
                contact_position=customer.contact_position,
                remarks=customer.remarks
            )
            self.db.add(db_customer)
            self.db.commit()
            self.db.refresh(db_customer)
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
            for key, value in update_data.items():
                setattr(db_customer, key, value)

            self.db.commit()
            self.db.refresh(db_customer)
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
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除客户失败 (id={customer_id}): {str(e)}")
            raise
