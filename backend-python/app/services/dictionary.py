
from sqlalchemy.orm import Session

from app.exceptions import NotFoundException
from app.models.dictionary import Dictionary
from app.repositories.dictionary import DictionaryRepository


class DictionaryService:
    def __init__(self, db: Session):
        self.repository = DictionaryRepository(db)

    def get_all(
        self,
        page: int = 0,
        size: int = 10,
        dict_type: str | None = None
    ) -> tuple[list[Dictionary], int]:
        return self.repository.find_all(page, size, dict_type)

    def get_by_type(self, dict_type: str) -> list[Dictionary]:
        return self.repository.find_by_type(dict_type)

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

        return self.repository.create(dictionary)

    def update(self, id: int, dto: dict) -> Dictionary:
        existing_dictionary = self.get_by_id(id)

        existing_dictionary.dict_type = dto.get('dict_type', existing_dictionary.dict_type)
        existing_dictionary.dict_key = dto.get('dict_key', existing_dictionary.dict_key)
        existing_dictionary.dict_value = dto.get('dict_value', existing_dictionary.dict_value)
        existing_dictionary.dict_label = dto.get('dict_label', existing_dictionary.dict_label)
        existing_dictionary.sort_order = dto.get('sort_order', existing_dictionary.sort_order)
        existing_dictionary.is_active = dto.get('is_active', existing_dictionary.is_active)

        return self.repository.update(existing_dictionary)

    def delete(self, id: int) -> None:
        dictionary = self.get_by_id(id)
        self.repository.delete(dictionary)

    def get_all_unpaginated(self, dict_type: str | None = None) -> list[Dictionary]:
        return self.repository.find_all_unpaginated(dict_type)
