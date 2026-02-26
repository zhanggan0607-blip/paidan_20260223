# -*- coding: utf-8 -*-
"""
统一权限配置模块
集中管理所有角色、权限和菜单配置
"""

from typing import List, Dict, Set, Optional
from dataclasses import dataclass, field
from enum import Enum


class RoleCode(str, Enum):
    """角色代码枚举"""
    ADMIN = '管理员'
    DEPARTMENT_MANAGER = '部门经理'
    MATERIAL_MANAGER = '材料员'
    EMPLOYEE = '运维人员'


@dataclass
class RoleConfig:
    """角色配置数据类"""
    code: str
    name: str
    level: int
    description: str = ''


ROLE_CONFIGS: Dict[str, RoleConfig] = {
    RoleCode.ADMIN.value: RoleConfig(
        code=RoleCode.ADMIN.value,
        name='管理员',
        level=100,
        description='系统管理员，拥有所有权限'
    ),
    RoleCode.DEPARTMENT_MANAGER.value: RoleConfig(
        code=RoleCode.DEPARTMENT_MANAGER.value,
        name='部门经理',
        level=70,
        description='部门经理，可管理项目和人员'
    ),
    RoleCode.MATERIAL_MANAGER.value: RoleConfig(
        code=RoleCode.MATERIAL_MANAGER.value,
        name='材料员',
        level=50,
        description='材料管理员，管理备品备件'
    ),
    RoleCode.EMPLOYEE.value: RoleConfig(
        code=RoleCode.EMPLOYEE.value,
        name='运维人员',
        level=10,
        description='普通员工，执行维保任务'
    ),
}

ALL_ROLES: List[str] = list(ROLE_CONFIGS.keys())

MANAGER_ROLES: List[str] = [
    RoleCode.ADMIN.value,
    RoleCode.DEPARTMENT_MANAGER.value,
]

ADMIN_ROLES: List[str] = [RoleCode.ADMIN.value]

PROJECT_MANAGEMENT_ROLES: List[str] = [
    RoleCode.ADMIN.value,
    RoleCode.DEPARTMENT_MANAGER.value,
]

PERSONNEL_MANAGEMENT_ROLES: List[str] = [
    RoleCode.ADMIN.value,
    RoleCode.DEPARTMENT_MANAGER.value,
]

SPARE_PARTS_MANAGEMENT_ROLES: List[str] = [
    RoleCode.ADMIN.value,
    RoleCode.DEPARTMENT_MANAGER.value,
    RoleCode.MATERIAL_MANAGER.value,
]

WORK_ORDER_VIEW_ROLES: List[str] = [
    RoleCode.ADMIN.value,
    RoleCode.DEPARTMENT_MANAGER.value,
    RoleCode.EMPLOYEE.value,
]

WORK_ORDER_APPROVE_ROLES: List[str] = [
    RoleCode.ADMIN.value,
    RoleCode.DEPARTMENT_MANAGER.value,
]

STATISTICS_VIEW_ROLES: List[str] = [
    RoleCode.ADMIN.value,
    RoleCode.DEPARTMENT_MANAGER.value,
    RoleCode.EMPLOYEE.value,
]

MAINTENANCE_LOG_FILL_ROLES: List[str] = [
    RoleCode.ADMIN.value,
    RoleCode.DEPARTMENT_MANAGER.value,
    RoleCode.EMPLOYEE.value,
]

MAINTENANCE_LOG_VIEW_ROLES: List[str] = [
    RoleCode.ADMIN.value,
    RoleCode.DEPARTMENT_MANAGER.value,
    RoleCode.EMPLOYEE.value,
]

WEEKLY_REPORT_FILL_ROLES: List[str] = [
    RoleCode.ADMIN.value,
    RoleCode.DEPARTMENT_MANAGER.value,
]

WEEKLY_REPORT_VIEW_ROLES: List[str] = [
    RoleCode.ADMIN.value,
    RoleCode.DEPARTMENT_MANAGER.value,
]


@dataclass
class PermissionConfig:
    """权限配置数据类"""
    id: str
    name: str
    description: str
    allowed_roles: List[str] = field(default_factory=list)


PERMISSION_CONFIGS: Dict[str, PermissionConfig] = {
    'view_statistics': PermissionConfig(
        id='view_statistics',
        name='查看统计',
        description='查看统计分析数据',
        allowed_roles=STATISTICS_VIEW_ROLES
    ),
    'view_project_management': PermissionConfig(
        id='view_project_management',
        name='项目管理',
        description='查看和管理项目信息、维保计划',
        allowed_roles=PROJECT_MANAGEMENT_ROLES
    ),
    'view_personnel': PermissionConfig(
        id='view_personnel',
        name='人员管理',
        description='查看和管理人员信息',
        allowed_roles=PERSONNEL_MANAGEMENT_ROLES
    ),
    'view_spare_parts_stock': PermissionConfig(
        id='view_spare_parts_stock',
        name='备件库存',
        description='查看和管理备品备件库存',
        allowed_roles=SPARE_PARTS_MANAGEMENT_ROLES
    ),
    'view_spare_parts_issue': PermissionConfig(
        id='view_spare_parts_issue',
        name='备件领用',
        description='领用备品备件',
        allowed_roles=SPARE_PARTS_MANAGEMENT_ROLES + [RoleCode.EMPLOYEE.value]
    ),
    'view_repair_tools_stock': PermissionConfig(
        id='view_repair_tools_stock',
        name='工具库存',
        description='查看和管理维修工具库存',
        allowed_roles=SPARE_PARTS_MANAGEMENT_ROLES
    ),
    'view_repair_tools_issue': PermissionConfig(
        id='view_repair_tools_issue',
        name='工具领用',
        description='领用维修工具',
        allowed_roles=SPARE_PARTS_MANAGEMENT_ROLES + [RoleCode.EMPLOYEE.value]
    ),
    'view_work_order': PermissionConfig(
        id='view_work_order',
        name='工单查看',
        description='查看工单列表和详情',
        allowed_roles=WORK_ORDER_VIEW_ROLES
    ),
    'approve_periodic_inspection': PermissionConfig(
        id='approve_periodic_inspection',
        name='审批巡检单',
        description='审批定期巡检工单',
        allowed_roles=WORK_ORDER_APPROVE_ROLES
    ),
    'approve_temporary_repair': PermissionConfig(
        id='approve_temporary_repair',
        name='审批维修单',
        description='审批临时维修工单',
        allowed_roles=WORK_ORDER_APPROVE_ROLES
    ),
    'approve_spot_work': PermissionConfig(
        id='approve_spot_work',
        name='审批零星用工单',
        description='审批零星用工工单',
        allowed_roles=WORK_ORDER_APPROVE_ROLES
    ),
    'fill_maintenance_log': PermissionConfig(
        id='fill_maintenance_log',
        name='填写维保日志',
        description='填写维保日志',
        allowed_roles=MAINTENANCE_LOG_FILL_ROLES
    ),
    'view_maintenance_log': PermissionConfig(
        id='view_maintenance_log',
        name='查看维保日志',
        description='查看维保日志',
        allowed_roles=MAINTENANCE_LOG_VIEW_ROLES
    ),
    'view_all_maintenance_log': PermissionConfig(
        id='view_all_maintenance_log',
        name='查看所有维保日志',
        description='查看所有人的维保日志',
        allowed_roles=PROJECT_MANAGEMENT_ROLES
    ),
    'fill_weekly_report': PermissionConfig(
        id='fill_weekly_report',
        name='填写周报',
        description='填写部门周报',
        allowed_roles=WEEKLY_REPORT_FILL_ROLES
    ),
    'view_weekly_report': PermissionConfig(
        id='view_weekly_report',
        name='查看周报',
        description='查看部门周报',
        allowed_roles=WEEKLY_REPORT_VIEW_ROLES
    ),
    'view_alerts': PermissionConfig(
        id='view_alerts',
        name='查看提醒',
        description='查看超期/临期提醒',
        allowed_roles=STATISTICS_VIEW_ROLES
    ),
    'view_system_management': PermissionConfig(
        id='view_system_management',
        name='系统管理',
        description='系统管理功能（客户、巡检事项等）',
        allowed_roles=PROJECT_MANAGEMENT_ROLES
    ),
    'delete_personnel': PermissionConfig(
        id='delete_personnel',
        name='删除人员',
        description='删除人员信息',
        allowed_roles=[RoleCode.ADMIN.value]
    ),
    'edit_personnel_role': PermissionConfig(
        id='edit_personnel_role',
        name='修改人员角色',
        description='修改人员角色',
        allowed_roles=[RoleCode.ADMIN.value]
    ),
}


def has_permission(role: Optional[str], permission_id: str) -> bool:
    """
    检查角色是否有指定权限
    
    Args:
        role: 用户角色
        permission_id: 权限ID
        
    Returns:
        bool: 是否有权限
    """
    if not role:
        return False
    
    permission = PERMISSION_CONFIGS.get(permission_id)
    if not permission:
        return False
    
    return role in permission.allowed_roles


def get_allowed_permissions(role: str) -> List[str]:
    """
    获取角色的所有权限
    
    Args:
        role: 用户角色
        
    Returns:
        List[str]: 权限ID列表
    """
    return [
        perm_id for perm_id, perm in PERMISSION_CONFIGS.items()
        if role in perm.allowed_roles
    ]


def is_manager_role(role: Optional[str]) -> bool:
    """
    检查是否为管理层角色
    
    Args:
        role: 用户角色
        
    Returns:
        bool: 是否为管理层
    """
    return role in MANAGER_ROLES if role else False


def is_admin_role(role: Optional[str]) -> bool:
    """
    检查是否为管理员角色
    
    Args:
        role: 用户角色
        
    Returns:
        bool: 是否为管理员
    """
    return role in ADMIN_ROLES if role else False


def get_role_level(role: Optional[str]) -> int:
    """
    获取角色级别
    
    Args:
        role: 用户角色
        
    Returns:
        int: 角色级别，级别越高权限越大
    """
    if not role:
        return 0
    
    config = ROLE_CONFIGS.get(role)
    return config.level if config else 0


def can_edit_personnel(current_role: str, target_role: str, 
                       current_department: str = '', target_department: str = '') -> bool:
    """
    检查是否可以编辑目标人员
    
    Args:
        current_role: 当前用户角色
        target_role: 目标人员角色
        current_department: 当前用户部门
        target_department: 目标人员部门
        
    Returns:
        bool: 是否可以编辑
    """
    if current_role == RoleCode.ADMIN.value:
        return True
    
    if current_role == RoleCode.DEPARTMENT_MANAGER.value:
        if current_department and target_department == current_department:
            return True
    
    return False


def can_delete_personnel(current_role: str) -> bool:
    """
    检查是否可以删除人员
    
    Args:
        current_role: 当前用户角色
        
    Returns:
        bool: 是否可以删除
    """
    return current_role == RoleCode.ADMIN.value


def get_personnel_filter_condition(current_role: str, current_department: str = '') -> Dict:
    """
    获取人员列表过滤条件
    
    Args:
        current_role: 当前用户角色
        current_department: 当前用户部门
        
    Returns:
        Dict: 过滤条件
    """
    if current_role == RoleCode.ADMIN.value:
        return {'filter': 'all'}
    
    if current_role == RoleCode.DEPARTMENT_MANAGER.value:
        return {'filter': 'all'}
    
    return {'filter': 'none'}
