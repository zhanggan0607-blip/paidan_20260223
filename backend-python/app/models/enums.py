from enum import Enum


class WorkOrderStatus(str, Enum):
    IN_PROGRESS = '执行中'
    PENDING_CONFIRM = '待确认'
    COMPLETED = '已完成'
    REJECTED = '已退回'


class UserRole(str, Enum):
    ADMIN = '管理员'
    DEPARTMENT_MANAGER = '部门经理'
    SUPERVISOR = '主管'
    MATERIAL_MANAGER = '材料员'
    EMPLOYEE = '运维人员'


ADMIN_ROLES = [UserRole.ADMIN, UserRole.DEPARTMENT_MANAGER, UserRole.SUPERVISOR]
MANAGER_ROLES = [UserRole.ADMIN, UserRole.DEPARTMENT_MANAGER]
