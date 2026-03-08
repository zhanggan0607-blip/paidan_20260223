import logging

from sqlalchemy.orm import Session

from app.repositories.dictionary import DictionaryRepository

logger = logging.getLogger(__name__)


class DictionaryHelper:
    """字典工具类，用于获取字典的默认值"""

    _cache = {}

    @classmethod
    def get_default_value(cls, db: Session, dict_type: str, dict_key: str) -> str:
        """获取字典的默认值"""
        cache_key = f"{dict_type}:{dict_key}"

        if cache_key in cls._cache:
            return cls._cache[cache_key]

        try:
            repository = DictionaryRepository(db)
            dictionary = repository.find_by_type_and_key(dict_type, dict_key)

            if dictionary:
                value = dictionary.dict_value
                cls._cache[cache_key] = value
                return value
            else:
                logger.warning(f"字典不存在: dict_type={dict_type}, dict_key={dict_key}")
                return ""
        except Exception as e:
            logger.error(f"获取字典默认值失败: {str(e)}")
            return ""


def get_default_temporary_repair_status(db: Session) -> str:
    """获取临时维修单默认状态"""
    value = DictionaryHelper.get_default_value(db, 'temporary_repair_status', 'not_started')
    return value if value else '执行中'


def get_default_spot_work_status(db: Session) -> str:
    """获取零星用工单默认状态"""
    value = DictionaryHelper.get_default_value(db, 'spot_work_status', 'not_started')
    return value if value else '执行中'


def get_default_periodic_inspection_status(db: Session) -> str:
    """获取定期巡检单默认状态"""
    value = DictionaryHelper.get_default_value(db, 'periodic_inspection_status', 'not_started')
    return value if value else '执行中'
