from app.utils.logging_config import get_logger

from fastapi import HTTPException, status

from app.dependencies import UserInfo, check_data_access, get_current_user_required, get_manager_user
from app.models.enums import WorkOrderStatus

logger = get_logger(__name__)


def validate_reject_reason(reason: str | None) -> str:
    if not reason or len(reason.strip()) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请输入工单退回原因，至少10个字符"
        )
    if len(reason.strip()) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="退回原因不能超过500个字符"
        )
    return reason.strip()


def submit_work_order(
    id: int,
    service,
    user_info: UserInfo,
    partial_update_class: type
):
    existing = service.get_by_id(id)
    if not check_data_access(user_info, existing.maintenance_personnel):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权提交此工单"
        )
    entity = service.partial_update(
        id,
        partial_update_class(status=WorkOrderStatus.PENDING_CONFIRM.value),
        user_info.id,
        user_info.name
    )
    return entity


def recall_work_order(
    id: int,
    service,
    user_info: UserInfo,
    partial_update_class: type
):
    existing = service.get_by_id(id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工单不存在"
        )
    if existing.status != WorkOrderStatus.PENDING_CONFIRM.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有待确认状态的工单才能撤回"
        )
    if not check_data_access(user_info, existing.maintenance_personnel):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权撤回此工单"
        )
    entity = service.partial_update(
        id,
        partial_update_class(status=WorkOrderStatus.IN_PROGRESS.value),
        user_info.id,
        user_info.name
    )
    return entity


def approve_work_order(
    id: int,
    dto,
    service,
    user_info: UserInfo,
    partial_update_class: type
):
    if dto.approved:
        entity = service.partial_update(
            id,
            partial_update_class(status=WorkOrderStatus.COMPLETED.value),
            user_info.id,
            user_info.name
        )
        return entity, "审批通过"
    else:
        validate_reject_reason(dto.reject_reason)
        entity = service.partial_update(
            id,
            partial_update_class(
                status=WorkOrderStatus.REJECTED.value,
                reject_reason=dto.reject_reason
            ),
            user_info.id,
            user_info.name
        )
        return entity, "已退回"
