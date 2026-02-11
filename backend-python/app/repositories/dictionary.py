from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.dictionary import Dictionary
import logging

logger = logging.getLogger(__name__)


class DictionaryRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, id: int) -> Optional[Dictionary]:
        try:
            return self.db.query(Dictionary).filter(Dictionary.id == id).first()
        except Exception as e:
            logger.error(f"查询字典失败 (id={id}): {str(e)}")
            raise

    def find_by_type(self, dict_type: str) -> List[Dictionary]:
        try:
            return self.db.query(Dictionary).filter(
                Dictionary.dict_type == dict_type,
                Dictionary.is_active == True
            ).order_by(Dictionary.sort_order.asc()).all()
        except Exception as e:
            logger.error(f"查询字典列表失败 (dict_type={dict_type}): {str(e)}")
            raise

    def find_by_type_and_key(self, dict_type: str, dict_key: str) -> Optional[Dictionary]:
        try:
            return self.db.query(Dictionary).filter(
                Dictionary.dict_type == dict_type,
                Dictionary.dict_key == dict_key
            ).first()
        except Exception as e:
            logger.error(f"查询字典失败 (dict_type={dict_type}, dict_key={dict_key}): {str(e)}")
            raise

    def find_all(
        self,
        page: int = 0,
        size: int = 10,
        dict_type: Optional[str] = None
    ) -> tuple[List[Dictionary], int]:
        try:
            query = self.db.query(Dictionary)

            if dict_type:
                query = query.filter(Dictionary.dict_type == dict_type)

            total = query.count()
            items = query.order_by(Dictionary.dict_type.asc(), Dictionary.sort_order.asc()).offset(page * size).limit(size).all()

            return items, total
        except Exception as e:
            logger.error(f"查询字典列表失败: {str(e)}")
            raise

    def find_all_unpaginated(self, dict_type: Optional[str] = None) -> List[Dictionary]:
        try:
            query = self.db.query(Dictionary)

            if dict_type:
                query = query.filter(Dictionary.dict_type == dict_type)

            return query.order_by(Dictionary.dict_type.asc(), Dictionary.sort_order.asc()).all()
        except Exception as e:
            logger.error(f"查询所有字典失败: {str(e)}")
            raise

    def create(self, dictionary: Dictionary) -> Dictionary:
        try:
            self.db.add(dictionary)
            self.db.commit()
            self.db.refresh(dictionary)
            return dictionary
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建字典失败: {str(e)}")
            raise

    def update(self, dictionary: Dictionary) -> Dictionary:
        try:
            self.db.commit()
            self.db.refresh(dictionary)
            return dictionary
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新字典失败: {str(e)}")
            raise

    def delete(self, dictionary: Dictionary) -> None:
        try:
            self.db.delete(dictionary)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除字典失败: {str(e)}")
            raise
