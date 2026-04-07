import logging

from sqlalchemy.orm import Session

from app.models.customer_contact import CustomerContact
from app.schemas.customer_contact import CustomerContactCreate, CustomerContactUpdate

logger = logging.getLogger(__name__)


class CustomerContactRepository:
    """
    客户联系人数据访问层
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_customer_id(self, customer_id: int) -> list[CustomerContact]:
        """
        根据客户ID获取所有联系人
        @param customer_id: 客户ID
        @return: 联系人列表
        """
        try:
            return self.db.query(CustomerContact).filter(
                CustomerContact.customer_id == customer_id
            ).order_by(CustomerContact.created_at.asc()).all()
        except Exception as e:
            logger.error(f"查询客户联系人失败 (customer_id={customer_id}): {str(e)}")
            raise

    def get_by_id(self, contact_id: int) -> CustomerContact | None:
        """
        根据ID获取联系人
        @param contact_id: 联系人ID
        @return: 联系人对象
        """
        try:
            return self.db.query(CustomerContact).filter(
                CustomerContact.id == contact_id
            ).first()
        except Exception as e:
            logger.error(f"查询联系人失败 (id={contact_id}): {str(e)}")
            raise

    def create(self, customer_id: int, contact: CustomerContactCreate) -> CustomerContact:
        """
        创建联系人
        @param customer_id: 客户ID
        @param contact: 联系人创建数据
        @return: 创建的联系人对象
        """
        try:
            db_contact = CustomerContact(
                customer_id=customer_id,
                contact_person=contact.contact_person,
                phone=contact.phone,
                contact_position=contact.contact_position,
                remarks=contact.remarks
            )
            self.db.add(db_contact)
            self.db.flush()
            return db_contact
        except Exception as e:
            logger.error(f"创建联系人失败: {str(e)}")
            raise

    def update(self, contact_id: int, contact: CustomerContactUpdate) -> CustomerContact | None:
        """
        更新联系人
        @param contact_id: 联系人ID
        @param contact: 联系人更新数据
        @return: 更新后的联系人对象
        """
        try:
            db_contact = self.get_by_id(contact_id)
            if not db_contact:
                return None

            update_data = contact.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_contact, key, value)

            self.db.flush()
            return db_contact
        except Exception as e:
            logger.error(f"更新联系人失败 (id={contact_id}): {str(e)}")
            raise

    def delete(self, contact_id: int) -> bool:
        """
        删除联系人
        @param contact_id: 联系人ID
        @return: 是否删除成功
        """
        try:
            db_contact = self.get_by_id(contact_id)
            if not db_contact:
                return False

            self.db.delete(db_contact)
            self.db.flush()
            return True
        except Exception as e:
            logger.error(f"删除联系人失败 (id={contact_id}): {str(e)}")
            raise

    def delete_by_customer_id(self, customer_id: int) -> int:
        """
        删除客户的所有联系人
        @param customer_id: 客户ID
        @return: 删除的数量
        """
        try:
            result = self.db.query(CustomerContact).filter(
                CustomerContact.customer_id == customer_id
            ).delete()
            self.db.flush()
            return result
        except Exception as e:
            logger.error(f"删除客户联系人失败 (customer_id={customer_id}): {str(e)}")
            raise

    def bulk_create(self, customer_id: int, contacts: list[CustomerContactCreate]) -> list[CustomerContact]:
        """
        批量创建联系人
        @param customer_id: 客户ID
        @param contacts: 联系人创建数据列表
        @return: 创建的联系人列表
        """
        try:
            db_contacts = []
            for contact in contacts:
                db_contact = CustomerContact(
                    customer_id=customer_id,
                    contact_person=contact.contact_person,
                    phone=contact.phone,
                    contact_position=contact.contact_position,
                    remarks=contact.remarks
                )
                self.db.add(db_contact)
                db_contacts.append(db_contact)
            self.db.flush()
            return db_contacts
        except Exception as e:
            logger.error(f"批量创建联系人失败: {str(e)}")
            raise
