# -*- coding: utf-8 -*-
"""
枚举定义模块
统一管理系统中的枚举值
"""

from enum import Enum


class WorkOrderStatus(str, Enum):
    """工单状态枚举"""
    PENDING = '待确认'
    NOT_ISSUED = '未下发'
    NOT_STARTED = '未进行'
    IN_PROGRESS = '执行中'
    WAITING_APPROVAL = '待审批'
    COMPLETED = '已完成'
    CONFIRMED = '已确认'
    APPROVED = '已审批'
    REJECTED = '已退回'
    WAITING_EXECUTE = '待执行'
    
    @classmethod
    def get_valid_statuses(cls) -> list:
        """获取有效状态列表（未完成）"""
        return [cls.PENDING.value, cls.NOT_ISSUED.value, cls.NOT_STARTED.value, 
                cls.WAITING_APPROVAL.value, cls.REJECTED.value, cls.WAITING_EXECUTE.value,
                cls.CONFIRMED.value, cls.IN_PROGRESS.value, '待确认']
    
    @classmethod
    def get_completed_statuses(cls) -> list:
        """获取已完成状态列表"""
        return [cls.COMPLETED.value, cls.CONFIRMED.value, cls.APPROVED.value]


class WorkOrderType(str, Enum):
    """工单类型枚举"""
    PERIODIC_INSPECTION = '定期巡检'
    TEMPORARY_REPAIR = '临时维修'
    SPOT_WORK = '零星用工'
    MAINTENANCE_PLAN = '维保计划'
    
    @classmethod
    def get_all_types(cls) -> list:
        """获取所有工单类型"""
        return [cls.PERIODIC_INSPECTION.value, cls.TEMPORARY_REPAIR.value, 
                cls.SPOT_WORK.value, cls.MAINTENANCE_PLAN.value]


class UserRole(str, Enum):
    """用户角色枚举"""
    ADMIN = '管理员'
    MANAGER = '部门经理'
    MATERIAL_MANAGER = '材料员'
    WORKER = '运维人员'
    
    @classmethod
    def get_all_roles(cls) -> list:
        """获取所有角色"""
        return [cls.ADMIN.value, cls.MANAGER.value, cls.MATERIAL_MANAGER.value, cls.WORKER.value]
    
    @classmethod
    def get_manager_roles(cls) -> list:
        """获取管理员角色列表"""
        return [cls.ADMIN.value, cls.MANAGER.value, '主管']
    
    @classmethod
    def is_manager(cls, role: str) -> bool:
        """判断是否为管理员角色"""
        return role in cls.get_manager_roles()


class WorkOrderPrefix(str, Enum):
    """工单编号前缀枚举"""
    INSPECTION = 'XJ'
    REPAIR = 'WX'
    SPOT_WORK = 'YG'
    
    @classmethod
    def get_prefix_by_type(cls, order_type: str) -> str:
        """根据工单类型获取前缀"""
        type_prefix_map = {
            'inspection': cls.INSPECTION.value,
            'repair': cls.REPAIR.value,
            'spotwork': cls.SPOT_WORK.value,
            WorkOrderType.PERIODIC_INSPECTION.value: cls.INSPECTION.value,
            WorkOrderType.TEMPORARY_REPAIR.value: cls.REPAIR.value,
            WorkOrderType.SPOT_WORK.value: cls.SPOT_WORK.value,
        }
        return type_prefix_map.get(order_type, '')


class InspectionResult(str, Enum):
    """巡检结果枚举"""
    NORMAL = '正常'
    ABNORMAL = '异常'
    PENDING = '待检'
    
    @classmethod
    def get_all_results(cls) -> list:
        """获取所有巡检结果"""
        return [cls.NORMAL.value, cls.ABNORMAL.value, cls.PENDING.value]


class Priority(str, Enum):
    """优先级枚举"""
    HIGH = '高'
    MEDIUM = '中'
    LOW = '低'
    
    @classmethod
    def get_all_priorities(cls) -> list:
        """获取所有优先级"""
        return [cls.HIGH.value, cls.MEDIUM.value, cls.LOW.value]
