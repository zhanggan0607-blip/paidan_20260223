import logging

from sqlalchemy.orm import Session

from app.models.personnel import Personnel

logger = logging.getLogger(__name__)


class PersonnelRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, id: int) -> Personnel | None:
        try:
            return self.db.query(Personnel).filter(Personnel.id == id).first()
        except Exception as e:
            logger.error(f"查询人员信息失败 (id={id}): {str(e)}")
            raise

    def find_by_name(self, name: str) -> Personnel | None:
        try:
            return self.db.query(Personnel).filter(Personnel.name == name).first()
        except Exception as e:
            logger.error(f"查询人员信息失败 (name={name}): {str(e)}")
            raise

    def find_all(
        self,
        page: int = 0,
        size: int = 10,
        name: str | None = None,
        department: str | None = None,
        current_user_role: str | None = None,
        current_user_department: str | None = None
    ) -> tuple[list[Personnel], int]:
        try:
            query = self.db.query(Personnel)

            if name:
                query = query.filter(Personnel.name.like(f"%{name}%"))

            if department:
                query = query.filter(Personnel.department.like(f"%{department}%"))

            if current_user_role and current_user_role != '管理员':
                if current_user_role == '部门经理':
                    pass
                else:
                    query = query.filter(Personnel.id == -1)

            total = query.count()
            items = query.order_by(Personnel.created_at.desc()).offset(page * size).limit(size).all()

            return items, total
        except Exception as e:
            logger.error(f"查询人员信息列表失败: {str(e)}")
            raise

    def find_all_unpaginated(self) -> list[Personnel]:
        try:
            return self.db.query(Personnel).order_by(Personnel.created_at.desc()).all()
        except Exception as e:
            logger.error(f"查询所有人员信息失败: {str(e)}")
            raise

    def create(self, personnel: Personnel) -> Personnel:
        try:
            self.db.add(personnel)
            self.db.commit()
            self.db.refresh(personnel)
            return personnel
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建人员信息失败: {str(e)}")
            raise

    def update(self, personnel: Personnel) -> Personnel:
        try:
            self.db.commit()
            self.db.refresh(personnel)
            return personnel
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新人员信息失败: {str(e)}")
            raise

    def delete(self, personnel: Personnel) -> None:
        try:
            self.db.delete(personnel)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除人员信息失败: {str(e)}")
            raise
