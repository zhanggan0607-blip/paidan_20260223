"""
字典服务
提供字典数据的业务逻辑处理，支持Redis缓存
"""
import logging

from sqlalchemy.orm import Session

from app.exceptions import NotFoundException
from app.models.dictionary import Dictionary
from app.repositories.dictionary import DictionaryRepository
from app.services.base import BaseService
from app.services.cache import CacheService

logger = logging.getLogger(__name__)

CACHE_KEY_PREFIX = "dict"
CACHE_TTL = 3600


class DictionaryService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)
        self.repository = DictionaryRepository(db)
        self.cache = CacheService()

    def _invalidate_cache(self, dict_type: str | None = None):
        """
        清除字典缓存
        
        Args:
            dict_type: 字典类型，为None时清除所有字典缓存
        """
        if dict_type:
            self.cache.delete(f"{CACHE_KEY_PREFIX}:type:{dict_type}")
        else:
            self.cache.delete_pattern(f"{CACHE_KEY_PREFIX}:*")
        logger.debug(f"字典缓存已清除: {dict_type or 'all'}")

    def get_all(
        self,
        page: int = 0,
        size: int = 10,
        dict_type: str | None = None
    ) -> tuple[list[Dictionary], int]:
        return self.repository.find_all(page, size, dict_type)

    def get_by_type(self, dict_type: str) -> list[Dictionary]:
        """
        根据字典类型获取字典列表（带缓存）
        
        Args:
            dict_type: 字典类型
            
        Returns:
            字典列表
        """
        cache_key = f"{CACHE_KEY_PREFIX}:type:{dict_type}"
        
        cached = self.cache.get(cache_key)
        if cached is not None:
            return [Dictionary(**item) for item in cached]
        
        items = self.repository.find_by_type(dict_type)
        
        cache_data = [
            {
                'id': item.id,
                'dict_type': item.dict_type,
                'dict_key': item.dict_key,
                'dict_value': item.dict_value,
                'dict_label': item.dict_label,
                'sort_order': item.sort_order,
                'is_active': item.is_active,
            }
            for item in items
        ]
        self.cache.set(cache_key, cache_data, CACHE_TTL)
        
        return items

    def get_by_type_and_key(self, dict_type: str, dict_key: str) -> Dictionary:
        dictionary = self.repository.find_by_type_and_key(dict_type, dict_key)
        if not dictionary:
            raise NotFoundException(f"字典不存在 (dict_type={dict_type}, dict_key={dict_key})")
        return dictionary

    def get_by_id(self, id: int) -> Dictionary:
        dictionary = self.repository.find_by_id(id)
        if not dictionary:
            raise NotFoundException(f"字典不存在 (id={id})")
        return dictionary

    def create(self, dto: dict) -> Dictionary:
        dictionary = Dictionary(
            dict_type=dto['dict_type'],
            dict_key=dto['dict_key'],
            dict_value=dto['dict_value'],
            dict_label=dto['dict_label'],
            sort_order=dto.get('sort_order', 0),
            is_active=dto.get('is_active', True)
        )
        
        result = self.repository.create(dictionary)
        self.commit()
        self._invalidate_cache(dto['dict_type'])
        return result

    def update(self, id: int, dto: dict) -> Dictionary:
        existing_dictionary = self.get_by_id(id)
        old_dict_type = existing_dictionary.dict_type
        
        existing_dictionary.dict_type = dto.get('dict_type', existing_dictionary.dict_type)
        existing_dictionary.dict_key = dto.get('dict_key', existing_dictionary.dict_key)
        existing_dictionary.dict_value = dto.get('dict_value', existing_dictionary.dict_value)
        existing_dictionary.dict_label = dto.get('dict_label', existing_dictionary.dict_label)
        existing_dictionary.sort_order = dto.get('sort_order', existing_dictionary.sort_order)
        existing_dictionary.is_active = dto.get('is_active', existing_dictionary.is_active)
        
        result = self.repository.update(existing_dictionary)
        self.commit()
        
        self._invalidate_cache(old_dict_type)
        if dto.get('dict_type') and dto.get('dict_type') != old_dict_type:
            self._invalidate_cache(dto.get('dict_type'))
        
        return result

    def delete(self, id: int) -> None:
        dictionary = self.get_by_id(id)
        dict_type = dictionary.dict_type
        self.repository.delete(dictionary)
        self.commit()
        self._invalidate_cache(dict_type)

    def get_all_unpaginated(self, dict_type: str | None = None) -> list[Dictionary]:
        return self.repository.find_all_unpaginated(dict_type)
