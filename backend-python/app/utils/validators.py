"""
通用验证函数
统一管理数据验证逻辑
"""
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


def validate_maintenance_personnel(db: Session, personnel_name: str) -> None:
    """
    校验运维人员必须在 personnel 表中存在
    
    Args:
        db: 数据库会话
        personnel_name: 运维人员姓名
        
    Raises:
        HTTPException: 人员不存在时抛出
    """
    if not personnel_name:
        return
    
    from app.services.personnel import PersonnelService
    
    personnel_service = PersonnelService(db)
    if not personnel_service.validate_personnel_exists(personnel_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"运维人员'{personnel_name}'不存在于人员列表中，请先添加该人员"
        )


def validate_required_field(value: any, field_name: str) -> None:
    """
    校验必填字段
    
    Args:
        value: 字段值
        field_name: 字段名称
        
    Raises:
        HTTPException: 字段为空时抛出
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name}不能为空"
        )


def validate_id_exists(db: Session, model_class, id: int, entity_name: str = "记录") -> any:
    """
    校验 ID 对应的记录是否存在
    
    Args:
        db: 数据库会话
        model_class: 模型类
        id: 记录 ID
        entity_name: 实体名称（用于错误消息）
        
    Returns:
        查询到的实体
        
    Raises:
        HTTPException: 记录不存在时抛出
    """
    entity = db.query(model_class).filter(model_class.id == id).first()
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity_name}不存在"
        )
    return entity


def validate_status_transition(
    current_status: str,
    allowed_statuses: list,
    target_status: str,
    entity_name: str = "记录"
) -> None:
    """
    校验状态转换是否合法
    
    Args:
        current_status: 当前状态
        allowed_statuses: 允许转换的当前状态列表
        target_status: 目标状态
        entity_name: 实体名称（用于错误消息）
        
    Raises:
        HTTPException: 状态转换不合法时抛出
    """
    if current_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{entity_name}当前状态为'{current_status}'，无法执行此操作"
        )


def validate_pagination_params(page: int, size: int, max_size: int = 100) -> tuple:
    """
    校验分页参数
    
    Args:
        page: 页码
        size: 每页大小
        max_size: 最大每页大小
        
    Returns:
        (page, size) 校验后的参数
        
    Raises:
        HTTPException: 参数不合法时抛出
    """
    if page < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="页码不能小于0"
        )
    
    if size < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="每页大小不能小于1"
        )
    
    if size > max_size:
        size = max_size
    
    return page, size
