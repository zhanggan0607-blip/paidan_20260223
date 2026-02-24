"""
工具模块索引
统一导出所有工具函数和类
"""
from .auth_helper import (
    UserContext,
    get_user_context,
    get_user_name_and_role,
    is_user_manager,
    get_user_name,
    get_current_user_from_headers,
    MANAGER_ROLES
)
from .validators import (
    validate_maintenance_personnel,
    validate_required_field,
    validate_id_exists,
    validate_status_transition,
    validate_pagination_params
)
from .pagination import (
    PageMeta,
    PaginatedResult,
    build_paginated_response,
    build_paginated_result,
    calculate_total_pages,
    is_first_page,
    is_last_page
)
from .id_generator import (
    generate_order_no,
    generate_inspection_id,
    generate_repair_id,
    generate_work_id,
    generate_inbound_no,
    generate_outbound_no,
    generate_plan_id
)

__all__ = [
    'UserContext',
    'get_user_context',
    'get_user_name_and_role',
    'is_user_manager',
    'get_user_name',
    'get_current_user_from_headers',
    'MANAGER_ROLES',
    'validate_maintenance_personnel',
    'validate_required_field',
    'validate_id_exists',
    'validate_status_transition',
    'validate_pagination_params',
    'PageMeta',
    'PaginatedResult',
    'build_paginated_response',
    'build_paginated_result',
    'calculate_total_pages',
    'is_first_page',
    'is_last_page',
    'generate_order_no',
    'generate_inspection_id',
    'generate_repair_id',
    'generate_work_id',
    'generate_inbound_no',
    'generate_outbound_no',
    'generate_plan_id'
]
