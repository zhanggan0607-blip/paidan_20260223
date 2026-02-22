# -*- coding: utf-8 -*-
"""
软删除Mixin
提供软删除功能的基类
"""

from datetime import datetime
from sqlalchemy import Column, Boolean, DateTime, BigInteger
from sqlalchemy.sql import func


class SoftDeleteMixin:
    """
    软删除Mixin
    
    为模型提供软删除功能，包括：
    - is_deleted: 是否已删除
    - deleted_at: 删除时间
    - deleted_by: 删除人ID
    """
    is_deleted = Column(Boolean, default=False, comment="是否已删除")
    deleted_at = Column(DateTime, comment="删除时间")
    deleted_by = Column(BigInteger, comment="删除人ID")
    
    def soft_delete(self, user_id: int = None):
        """
        执行软删除
        
        Args:
            user_id: 执行删除的用户ID
        """
        self.is_deleted = True
        self.deleted_at = datetime.now()
        self.deleted_by = user_id
    
    def restore(self):
        """
        恢复已删除的记录
        """
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
    
    @classmethod
    def filter_active(cls, query):
        """
        过滤出未删除的记录
        
        Args:
            query: SQLAlchemy查询对象
            
        Returns:
            过滤后的查询对象
        """
        return query.filter(cls.is_deleted == False)


class AuditMixin:
    """
    审计Mixin
    
    为模型提供审计字段，包括：
    - created_by: 创建人ID
    - updated_by: 更新人ID
    """
    created_by = Column(BigInteger, comment="创建人ID")
    updated_by = Column(BigInteger, comment="更新人ID")


class SoftDeleteAuditMixin(SoftDeleteMixin, AuditMixin):
    """
    软删除和审计Mixin的组合
    
    同时提供软删除和审计功能
    """
    pass
