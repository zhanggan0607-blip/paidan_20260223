"""
软删除Mixin & 序列化Mixin
提供软删除功能和标准化序列化功能
"""

import json
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import ColumnProperty


class SoftDeleteMixin:
    is_deleted = Column(Boolean, default=False, comment="是否已删除")
    deleted_at = Column(DateTime, comment="删除时间")
    deleted_by = Column(BigInteger, comment="删除人ID")

    def soft_delete(self, user_id: int = None):
        self.is_deleted = True
        self.deleted_at = datetime.now()
        self.deleted_by = user_id

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None

    @classmethod
    def filter_active(cls, query):
        return query.filter(cls.is_deleted == False)


_EXCLUDE_COLUMNS = {'password_hash'}


class SerializationMixin:
    """
    标准化序列化Mixin

    提供统一的 to_dict() 方法，自动处理：
    - DateTime 字段序列化为 ISO 格式
    - JSONB 字段直接返回（无需 json.loads）
    - 排除敏感字段（如 password_hash）
    - 支持自定义排除字段和额外字段
    - 支持声明式日期格式化和关联字段

    类属性配置：
    - _exclude_from_dict: 排除的字段集合
    - _date_only_fields: 仅输出日期(YYYY-MM-DD)的字段集合
    - _relation_extras: 关联模型额外字段的映射 {输出字段名: (关联属性名, 关联模型字段名)}
    - _relation_overrides: 关联模型覆盖字段的映射 {当前字段名: (关联属性名, 关联模型字段名)}
      当关联对象存在时，用关联对象的字段值覆盖当前字段值
    """

    _JSON_LIKE_FIELDS = {'photos', 'images', 'inspection_items', 'work_content', 'check_items'}

    _exclude_from_dict: set = set()
    _date_only_fields: set = set()
    _relation_extras: dict = {}
    _relation_overrides: dict = {}

    def to_dict(self, exclude: set | None = None, extra: dict | None = None) -> dict:
        result = {}
        exclude_set = _EXCLUDE_COLUMNS | set(self._exclude_from_dict) | (exclude or set())

        mapper = self.__class__.__mapper__
        for column_property in mapper.iterate_properties:
            if not isinstance(column_property, ColumnProperty):
                continue
            key = column_property.key
            if key in exclude_set:
                continue

            value = getattr(self, key, None)

            if isinstance(value, datetime):
                if key in self._date_only_fields:
                    result[key] = value.strftime('%Y-%m-%d') if value else None
                else:
                    result[key] = value.isoformat()
            elif isinstance(value, list):
                result[key] = value
            elif isinstance(value, str) and self._should_parse_json(key, mapper):
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, (list, dict)):
                        result[key] = parsed
                    else:
                        result[key] = value
                except (json.JSONDecodeError, TypeError):
                    result[key] = value
            else:
                result[key] = value

        for field_name, (relation_attr, source_field) in self._relation_overrides.items():
            relation_obj = getattr(self, relation_attr, None)
            if relation_obj:
                override_value = getattr(relation_obj, source_field, None)
                if override_value is not None:
                    result[field_name] = override_value

        for field_name, (relation_attr, source_field) in self._relation_extras.items():
            relation_obj = getattr(self, relation_attr, None)
            if relation_obj:
                result[field_name] = getattr(relation_obj, source_field, '') or ''
            else:
                result[field_name] = ''

        if extra:
            result.update(extra)

        return result

    @staticmethod
    def _should_parse_json(key: str, mapper) -> bool:
        if key in SerializationMixin._JSON_LIKE_FIELDS:
            return True
        try:
            column = mapper.columns[key]
            return isinstance(column.type, JSONB)
        except (KeyError, AttributeError):
            return False
