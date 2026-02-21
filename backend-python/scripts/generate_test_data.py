"""
全流程测试数据生成脚本
按照业务流程生成完整的测试数据：
1. 操作类型数据
2. 巡检事项数据
3. 维保计划数据
4. 定期巡检工单及记录
5. 临时维修工单
6. 零星用工工单
7. 备品备件数据
8. 工单操作日志
"""

import sys
import os
import random
from datetime import datetime, timedelta
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import (
    ProjectInfo, Personnel, Customer,
    MaintenancePlan, WorkPlan, InspectionItem,
    PeriodicInspection, PeriodicInspectionRecord,
    TemporaryRepair, SpotWork, SpotWorkWorker,
    SparePartsStock, SparePartsInbound, SparePartsUsage,
    RepairToolsStock, RepairToolsIssue, RepairToolsInbound,
    WorkOrderOperationLog, OperationType
)

random.seed(42)

STATUS_WORKFLOW = {
    '未进行': ['待提交', '已提交', '已审批', '已退回'],
    '待提交': ['已提交', '已退回'],
    '已提交': ['已审批', '已退回'],
    '已退回': ['待提交', '已提交'],
    '已审批': []
}

OPERATION_TYPES_DATA = [
    {'type_code': 'CREATE', 'type_name': '创建', 'color_code': '#1890ff', 'sort_order': 1},
    {'type_code': 'SUBMIT', 'type_name': '提交', 'color_code': '#52c41a', 'sort_order': 2},
    {'type_code': 'APPROVE', 'type_name': '审批通过', 'color_code': '#13c2c2', 'sort_order': 3},
    {'type_code': 'REJECT', 'type_name': '退回', 'color_code': '#f5222d', 'sort_order': 4},
    {'type_code': 'MODIFY', 'type_name': '修改', 'color_code': '#faad14', 'sort_order': 5},
    {'type_code': 'DELETE', 'type_name': '删除', 'color_code': '#722ed1', 'sort_order': 6},
    {'type_code': 'ISSUE', 'type_name': '下发', 'color_code': '#eb2f96', 'sort_order': 7},
    {'type_code': 'COMPLETE', 'type_name': '完成', 'color_code': '#2f54eb', 'sort_order': 8},
]

INSPECTION_ITEMS_DATA = [
    {
        'item_code': 'XJ-001',
        'item_name': '监控系统',
        'item_type': '巡检',
        'level': 1,
        'parent_id': None,
        'check_content': None,
        'check_standard': None,
        'sort_order': 1,
        'children': [
            {
                'item_code': 'XJ-001-01',
                'item_name': '摄像头检查',
                'item_type': '巡检',
                'level': 2,
                'check_content': '检查摄像头画面是否清晰',
                'check_standard': '画面清晰无遮挡',
                'sort_order': 1,
                'children': [
                    {'item_code': 'XJ-001-01-01', 'item_name': '画面清晰度', 'item_type': '巡检', 'level': 3, 'check_content': '检查画面是否清晰', 'check_standard': '画面清晰', 'sort_order': 1},
                    {'item_code': 'XJ-001-01-02', 'item_name': '镜头清洁', 'item_type': '巡检', 'level': 3, 'check_content': '检查镜头是否有灰尘', 'check_standard': '镜头干净', 'sort_order': 2},
                ]
            },
            {
                'item_code': 'XJ-001-02',
                'item_name': '录像设备检查',
                'item_type': '巡检',
                'level': 2,
                'check_content': '检查录像设备运行状态',
                'check_standard': '设备正常运行',
                'sort_order': 2,
                'children': [
                    {'item_code': 'XJ-001-02-01', 'item_name': '硬盘状态', 'item_type': '巡检', 'level': 3, 'check_content': '检查硬盘是否正常', 'check_standard': '硬盘读写正常', 'sort_order': 1},
                    {'item_code': 'XJ-001-02-02', 'item_name': '存储空间', 'item_type': '巡检', 'level': 3, 'check_content': '检查存储空间是否充足', 'check_standard': '剩余空间大于20%', 'sort_order': 2},
                ]
            }
        ]
    },
    {
        'item_code': 'XJ-002',
        'item_name': '网络设备',
        'item_type': '巡检',
        'level': 1,
        'parent_id': None,
        'check_content': None,
        'check_standard': None,
        'sort_order': 2,
        'children': [
            {
                'item_code': 'XJ-002-01',
                'item_name': '交换机检查',
                'item_type': '巡检',
                'level': 2,
                'check_content': '检查交换机运行状态',
                'check_standard': '交换机正常运行',
                'sort_order': 1,
                'children': [
                    {'item_code': 'XJ-002-01-01', 'item_name': '端口状态', 'item_type': '巡检', 'level': 3, 'check_content': '检查各端口状态', 'check_standard': '端口指示灯正常', 'sort_order': 1},
                    {'item_code': 'XJ-002-01-02', 'item_name': '散热状态', 'item_type': '巡检', 'level': 3, 'check_content': '检查散热是否正常', 'check_standard': '风扇运转正常', 'sort_order': 2},
                ]
            },
            {
                'item_code': 'XJ-002-02',
                'item_name': '路由器检查',
                'item_type': '巡检',
                'level': 2,
                'check_content': '检查路由器运行状态',
                'check_standard': '路由器正常运行',
                'sort_order': 2,
                'children': [
                    {'item_code': 'XJ-002-02-01', 'item_name': '网络连接', 'item_type': '巡检', 'level': 3, 'check_content': '检查网络连接状态', 'check_standard': '网络连通正常', 'sort_order': 1},
                    {'item_code': 'XJ-002-02-02', 'item_name': '配置备份', 'item_type': '巡检', 'level': 3, 'check_content': '检查配置是否备份', 'check_standard': '配置已备份', 'sort_order': 2},
                ]
            }
        ]
    },
    {
        'item_code': 'XJ-003',
        'item_name': '服务器设备',
        'item_type': '巡检',
        'level': 1,
        'parent_id': None,
        'check_content': None,
        'check_standard': None,
        'sort_order': 3,
        'children': [
            {
                'item_code': 'XJ-003-01',
                'item_name': '服务器硬件检查',
                'item_type': '巡检',
                'level': 2,
                'check_content': '检查服务器硬件状态',
                'check_standard': '硬件运行正常',
                'sort_order': 1,
                'children': [
                    {'item_code': 'XJ-003-01-01', 'item_name': 'CPU状态', 'item_type': '巡检', 'level': 3, 'check_content': '检查CPU使用率', 'check_standard': '使用率低于80%', 'sort_order': 1},
                    {'item_code': 'XJ-003-01-02', 'item_name': '内存状态', 'item_type': '巡检', 'level': 3, 'check_content': '检查内存使用率', 'check_standard': '使用率低于80%', 'sort_order': 2},
                    {'item_code': 'XJ-003-01-03', 'item_name': '磁盘状态', 'item_type': '巡检', 'level': 3, 'check_content': '检查磁盘空间', 'check_standard': '剩余空间大于20%', 'sort_order': 3},
                ]
            }
        ]
    },
    {
        'item_code': 'WX-001',
        'item_name': '维修事项',
        'item_type': '维修',
        'level': 1,
        'parent_id': None,
        'check_content': None,
        'check_standard': None,
        'sort_order': 4,
        'children': [
            {
                'item_code': 'WX-001-01',
                'item_name': '设备故障维修',
                'item_type': '维修',
                'level': 2,
                'check_content': '设备故障诊断与修复',
                'check_standard': '设备恢复正常运行',
                'sort_order': 1,
                'children': [
                    {'item_code': 'WX-001-01-01', 'item_name': '故障诊断', 'item_type': '维修', 'level': 3, 'check_content': '诊断故障原因', 'check_standard': '准确找出故障原因', 'sort_order': 1},
                    {'item_code': 'WX-001-01-02', 'item_name': '故障修复', 'item_type': '维修', 'level': 3, 'check_content': '修复设备故障', 'check_standard': '设备恢复正常', 'sort_order': 2},
                ]
            }
        ]
    }
]

SPARE_PARTS_DATA = [
    {'product_name': '网线', 'brand': 'TP-LINK', 'model': 'CAT6-305M', 'unit': '箱', 'quantity': 10, 'status': '在库'},
    {'product_name': '交换机', 'brand': '华为', 'model': 'S5700-28P', 'unit': '台', 'quantity': 5, 'status': '在库'},
    {'product_name': '硬盘', 'brand': '希捷', 'model': 'ST4000NM0035', 'unit': '块', 'quantity': 8, 'status': '在库'},
    {'product_name': '摄像头', 'brand': '海康威视', 'model': 'DS-2CD2T47G2-L', 'unit': '个', 'quantity': 20, 'status': '在库'},
    {'product_name': '路由器', 'brand': 'TP-LINK', 'model': 'TL-R470GP-AC', 'unit': '台', 'quantity': 3, 'status': '在库'},
    {'product_name': '电源适配器', 'brand': '通用', 'model': '12V-2A', 'unit': '个', 'quantity': 15, 'status': '在库'},
    {'product_name': '光纤跳线', 'brand': '长飞', 'model': 'LC-LC-OM3', 'unit': '根', 'quantity': 30, 'status': '在库'},
    {'product_name': '网线水晶头', 'brand': '安普', 'model': 'RJ45', 'unit': '盒', 'quantity': 5, 'status': '在库'},
]

REPAIR_TOOLS_DATA = [
    {'tool_id': 'GJ-001', 'tool_name': '网线钳', 'category': '网络工具', 'specification': 'RJ45/RJ11', 'unit': '把', 'stock': 3, 'min_stock': 2, 'location': '工具柜A1'},
    {'tool_id': 'GJ-002', 'tool_name': '测线仪', 'category': '网络工具', 'specification': 'NF-468', 'unit': '台', 'stock': 2, 'min_stock': 1, 'location': '工具柜A1'},
    {'tool_id': 'GJ-003', 'tool_name': '万用表', 'category': '电工工具', 'specification': 'VC890C+', 'unit': '台', 'stock': 4, 'min_stock': 2, 'location': '工具柜A2'},
    {'tool_id': 'GJ-004', 'tool_name': '电烙铁', 'category': '焊接工具', 'specification': '60W', 'unit': '把', 'stock': 3, 'min_stock': 2, 'location': '工具柜A2'},
    {'tool_id': 'GJ-005', 'tool_name': '螺丝刀套装', 'category': '常用工具', 'specification': 'PH1-PH3', 'unit': '套', 'stock': 5, 'min_stock': 3, 'location': '工具柜B1'},
    {'tool_id': 'GJ-006', 'tool_name': '梯子', 'category': '登高工具', 'specification': '3米铝合金', 'unit': '把', 'stock': 2, 'min_stock': 1, 'location': '仓库角落'},
]

def generate_plan_id(prefix, project_id, date):
    """
    生成计划编号
    格式: 前缀 + 项目编号 + 年月日
    """
    date_str = date.strftime('%Y%m%d')
    return f"{prefix}-{project_id}-{date_str}"

def generate_work_order_no(prefix, project_id, date, seq):
    """
    生成工单编号
    格式: 前缀-项目编号-年月日序号
    """
    date_str = date.strftime('%Y%m%d')
    return f"{prefix}-{project_id}-{date_str}{seq:02d}"

def create_operation_types(db):
    """
    创建操作类型数据
    """
    print("正在创建操作类型数据...")
    created_count = 0
    for data in OPERATION_TYPES_DATA:
        existing = db.query(OperationType).filter(
            OperationType.type_code == data['type_code']
        ).first()
        if not existing:
            op_type = OperationType(**data)
            db.add(op_type)
            created_count += 1
    db.commit()
    print(f"操作类型数据创建完成，新增 {created_count} 条")
    return db.query(OperationType).all()

def create_inspection_items(db):
    """
    创建巡检事项数据（树形结构）
    """
    print("正在创建巡检事项数据...")
    created_count = 0
    
    def create_item_recursive(data, parent_id=None):
        nonlocal created_count
        existing = db.query(InspectionItem).filter(
            InspectionItem.item_code == data['item_code']
        ).first()
        if existing:
            item = existing
        else:
            item = InspectionItem(
                item_code=data['item_code'],
                item_name=data['item_name'],
                item_type=data['item_type'],
                level=data['level'],
                parent_id=parent_id,
                check_content=data.get('check_content'),
                check_standard=data.get('check_standard'),
                sort_order=data.get('sort_order', 0)
            )
            db.add(item)
            db.flush()
            created_count += 1
        
        if 'children' in data:
            for child in data['children']:
                create_item_recursive(child, item.id)
    
    for item_data in INSPECTION_ITEMS_DATA:
        create_item_recursive(item_data)
    
    db.commit()
    print(f"巡检事项数据创建完成，新增 {created_count} 条")
    return db.query(InspectionItem).filter(InspectionItem.level == 3).all()

def create_spare_parts(db):
    """
    创建备品备件数据
    """
    print("正在创建备品备件数据...")
    created_count = 0
    for data in SPARE_PARTS_DATA:
        existing = db.query(SparePartsStock).filter(
            SparePartsStock.product_name == data['product_name'],
            SparePartsStock.brand == data['brand'],
            SparePartsStock.model == data['model']
        ).first()
        if not existing:
            part = SparePartsStock(**data)
            db.add(part)
            created_count += 1
    db.commit()
    print(f"备品备件数据创建完成，新增 {created_count} 条")
    return db.query(SparePartsStock).all()

def create_repair_tools(db):
    """
    创建维修工具数据
    """
    print("正在创建维修工具数据...")
    created_count = 0
    for data in REPAIR_TOOLS_DATA:
        existing = db.query(RepairToolsStock).filter(
            RepairToolsStock.tool_id == data['tool_id']
        ).first()
        if not existing:
            tool = RepairToolsStock(**data)
            db.add(tool)
            created_count += 1
    db.commit()
    print(f"维修工具数据创建完成，新增 {created_count} 条")
    return db.query(RepairToolsStock).all()

def create_maintenance_plans(db, projects, personnels):
    """
    创建维保计划数据
    """
    print("正在创建维保计划数据...")
    created_count = 0
    plans = []
    
    managers = [p for p in personnels if p.role in ['管理员', '部门经理']]
    workers = [p for p in personnels if p.role == '运维人员']
    
    if not managers:
        managers = personnels[:1]
    if not workers:
        workers = personnels
    
    plan_types = ['定期巡检', '临时维修', '零星用工']
    today = datetime.now().date()
    
    for project in projects:
        if project.project_id.startswith('TEST'):
            continue
            
        for i, plan_type in enumerate(plan_types):
            plan_id = generate_plan_id(f"PLAN-{plan_type[:2]}", project.project_id, today - timedelta(days=i*7))
            
            existing = db.query(MaintenancePlan).filter(
                MaintenancePlan.plan_id == plan_id
            ).first()
            if existing:
                plans.append(existing)
                continue
            
            manager = random.choice(managers)
            worker = random.choice(workers)
            
            start_date = today - timedelta(days=i*7)
            end_date = start_date + timedelta(days=7)
            
            from sqlalchemy import text
            plan_data = {
                'plan_id': plan_id,
                'plan_name': f"{project.project_name}-{plan_type}计划",
                'project_id': project.project_id,
                'plan_type': plan_type,
                'equipment_id': f"EQ-{random.randint(1000, 9999)}",
                'equipment_name': f"{plan_type}设备{random.randint(1, 10)}",
                'equipment_model': f"Model-{random.choice(['A', 'B', 'C'])}{random.randint(100, 999)}",
                'equipment_location': f"{project.address[:50] if project.address else '机房'}-位置{random.randint(1, 5)}",
                'plan_start_date': datetime.combine(start_date, datetime.min.time()),
                'plan_end_date': datetime.combine(end_date, datetime.min.time()),
                'responsible_person': worker.name,
                'responsible_department': worker.department,
                'contact_info': worker.phone or '13800138000',
                'maintenance_content': f"{plan_type}设备日常维护保养",
                'maintenance_requirements': "按照标准流程执行",
                'maintenance_standard': "设备运行正常，无异常",
                'plan_status': '已下发',
                'execution_status': '未进行',
                'completion_rate': 0
            }
            
            conn = db.connection()
            result = conn.execute(text("""
                INSERT INTO maintenance_plan 
                (plan_id, plan_name, project_id, plan_type, equipment_id, equipment_name, 
                 equipment_model, equipment_location, plan_start_date, plan_end_date, 
                 responsible_person, responsible_department, contact_info, 
                 maintenance_content, maintenance_requirements, maintenance_standard, 
                 plan_status, execution_status, completion_rate, created_at, updated_at)
                VALUES 
                (:plan_id, :plan_name, :project_id, :plan_type, :equipment_id, :equipment_name, 
                 :equipment_model, :equipment_location, :plan_start_date, :plan_end_date, 
                 :responsible_person, :responsible_department, :contact_info, 
                 :maintenance_content, :maintenance_requirements, :maintenance_standard, 
                 :plan_status, :execution_status, :completion_rate, NOW(), NOW())
                RETURNING id
            """), plan_data)
            row = result.fetchone()
            plan_id_db = row[0] if row else None
            db.commit()
            
            plan = db.query(MaintenancePlan).filter(MaintenancePlan.id == plan_id_db).first() if plan_id_db else None
            if plan:
                plans.append(plan)
            created_count += 1
    
    print(f"维保计划数据创建完成，新增 {created_count} 条")
    return plans

def create_periodic_inspections(db, projects, plans, personnels, inspection_items):
    """
    创建定期巡检工单及记录
    """
    print("正在创建定期巡检工单数据...")
    created_count = 0
    record_count = 0
    
    workers = [p for p in personnels if p.role == '运维人员']
    if not workers:
        workers = personnels
    
    inspection_plans = [p for p in plans if p.plan_type == '定期巡检']
    today = datetime.now().date()
    
    statuses = ['未进行', '待提交', '已提交', '已审批', '已退回']
    status_weights = [0.1, 0.2, 0.3, 0.35, 0.05]
    
    for i, project in enumerate(projects):
        if project.project_id.startswith('TEST'):
            continue
            
        for j in range(3):
            seq = j + 1
            start_date = today - timedelta(days=j*14)
            end_date = start_date + timedelta(days=7)
            inspection_id = generate_work_order_no('XJ', project.project_id, start_date, seq)
            
            existing = db.query(PeriodicInspection).filter(
                PeriodicInspection.inspection_id == inspection_id
            ).first()
            if existing:
                continue
            
            plan = random.choice(inspection_plans) if inspection_plans else None
            worker = random.choice(workers)
            
            status = random.choices(statuses, weights=status_weights)[0]
            
            inspection = PeriodicInspection(
                inspection_id=inspection_id,
                plan_id=plan.plan_id if plan else None,
                project_id=project.project_id,
                project_name=project.project_name,
                plan_start_date=datetime.combine(start_date, datetime.min.time()),
                plan_end_date=datetime.combine(end_date, datetime.min.time()),
                client_name=project.client_name,
                maintenance_personnel=worker.name,
                status=status,
                filled_count=5 if status in ['已提交', '已审批'] else (3 if status == '已退回' else 0),
                total_count=5,
                execution_result='发现部分设备需要维护' if status in ['已提交', '已审批', '已退回'] else None,
                remarks='已按要求完成巡检' if status == '已审批' else ('需要补充现场照片' if status == '已退回' else None),
                signature='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==' if status == '已审批' else None,
                actual_completion_date=datetime.combine(end_date - timedelta(days=1), datetime.min.time()) if status == '已审批' else None
            )
            db.add(inspection)
            db.flush()
            created_count += 1
            
            for k, item in enumerate(inspection_items[:5]):
                record = PeriodicInspectionRecord(
                    inspection_id=inspection.inspection_id,
                    item_id=str(item.id),
                    item_name=item.item_name,
                    inspection_item=item.parent.item_name if item.parent else item.item_name,
                    inspection_content=item.check_content or '',
                    check_content=item.check_standard or '',
                    brief_description='正常' if status in ['已提交', '已审批'] else '',
                    equipment_name=f"设备{k+1}",
                    equipment_location=f"位置{k+1}",
                    inspected=status in ['已提交', '已审批'],
                    photos='[]',
                    inspection_result='正常' if status in ['已提交', '已审批'] else ''
                )
                db.add(record)
                record_count += 1
            
            create_operation_log(db, 'periodic_inspection', inspection.id, inspection.inspection_id, 
                               worker, 'CREATE', '创建定期巡检工单')
            
            if status in ['已提交', '已审批', '已退回']:
                create_operation_log(db, 'periodic_inspection', inspection.id, inspection.inspection_id,
                                   worker, 'SUBMIT', '提交定期巡检工单')
            
            if status == '已审批':
                manager = random.choice([p for p in personnels if p.role in ['管理员', '部门经理']] or personnels)
                create_operation_log(db, 'periodic_inspection', inspection.id, inspection.inspection_id,
                                   manager, 'APPROVE', '审批通过定期巡检工单')
            
            if status == '已退回':
                manager = random.choice([p for p in personnels if p.role in ['管理员', '部门经理']] or personnels)
                create_operation_log(db, 'periodic_inspection', inspection.id, inspection.inspection_id,
                                   manager, 'REJECT', '退回定期巡检工单，需要补充现场照片')
    
    db.commit()
    print(f"定期巡检工单数据创建完成，新增 {created_count} 条工单，{record_count} 条记录")
    return created_count

def create_temporary_repairs(db, projects, plans, personnels):
    """
    创建临时维修工单
    """
    print("正在创建临时维修工单数据...")
    created_count = 0
    
    workers = [p for p in personnels if p.role == '运维人员']
    if not workers:
        workers = personnels
    
    repair_plans = [p for p in plans if p.plan_type == '临时维修']
    today = datetime.now().date()
    
    statuses = ['未进行', '待提交', '已提交', '已审批', '已退回']
    status_weights = [0.1, 0.2, 0.3, 0.35, 0.05]
    
    fault_descriptions = [
        '摄像头画面模糊，需要清洁镜头',
        '交换机端口故障，需要更换端口',
        '服务器硬盘告警，需要检查硬盘状态',
        '网络连接中断，需要排查线路',
        '设备电源故障，需要更换电源适配器'
    ]
    
    solutions = [
        '已清洁镜头，画面恢复正常',
        '已更换至备用端口，网络恢复正常',
        '已检查硬盘，更换故障硬盘，系统运行正常',
        '已排查并修复线路故障，网络已恢复',
        '已更换电源适配器，设备运行正常'
    ]
    
    for i, project in enumerate(projects):
        if project.project_id.startswith('TEST'):
            continue
            
        for j in range(2):
            seq = j + 1
            start_date = today - timedelta(days=j*10)
            end_date = start_date + timedelta(days=3)
            repair_id = generate_work_order_no('WX', project.project_id, start_date, seq)
            
            existing = db.query(TemporaryRepair).filter(
                TemporaryRepair.repair_id == repair_id
            ).first()
            if existing:
                continue
            
            plan = random.choice(repair_plans) if repair_plans else None
            worker = random.choice(workers)
            
            status = random.choices(statuses, weights=status_weights)[0]
            fault_idx = random.randint(0, len(fault_descriptions) - 1)
            
            repair = TemporaryRepair(
                repair_id=repair_id,
                plan_id=plan.plan_id if plan else None,
                project_id=project.project_id,
                project_name=project.project_name,
                plan_start_date=datetime.combine(start_date, datetime.min.time()),
                plan_end_date=datetime.combine(end_date, datetime.min.time()),
                client_name=project.client_name,
                maintenance_personnel=worker.name,
                status=status,
                fault_description=fault_descriptions[fault_idx] if status != '未进行' else None,
                solution=solutions[fault_idx] if status in ['已提交', '已审批'] else None,
                photos='[]',
                signature='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==' if status == '已审批' else None,
                execution_date=datetime.combine(start_date + timedelta(days=1), datetime.min.time()) if status in ['已提交', '已审批'] else None,
                actual_completion_date=datetime.combine(end_date, datetime.min.time()) if status == '已审批' else None
            )
            db.add(repair)
            db.flush()
            created_count += 1
            
            create_operation_log(db, 'temporary_repair', repair.id, repair.repair_id,
                               worker, 'CREATE', '创建临时维修工单')
            
            if status in ['已提交', '已审批', '已退回']:
                create_operation_log(db, 'temporary_repair', repair.id, repair.repair_id,
                                   worker, 'SUBMIT', '提交临时维修工单')
            
            if status == '已审批':
                manager = random.choice([p for p in personnels if p.role in ['管理员', '部门经理']] or personnels)
                create_operation_log(db, 'temporary_repair', repair.id, repair.repair_id,
                                   manager, 'APPROVE', '审批通过临时维修工单')
            
            if status == '已退回':
                manager = random.choice([p for p in personnels if p.role in ['管理员', '部门经理']] or personnels)
                create_operation_log(db, 'temporary_repair', repair.id, repair.repair_id,
                                   manager, 'REJECT', '退回临时维修工单，需要补充故障描述')
    
    db.commit()
    print(f"临时维修工单数据创建完成，新增 {created_count} 条")
    return created_count

def create_spot_works(db, projects, plans, personnels):
    """
    创建零星用工工单
    """
    print("正在创建零星用工工单数据...")
    created_count = 0
    worker_count = 0
    
    workers = [p for p in personnels if p.role == '运维人员']
    if not workers:
        workers = personnels
    
    spot_plans = [p for p in plans if p.plan_type == '零星用工']
    today = datetime.now().date()
    
    statuses = ['未进行', '待提交', '已提交', '已审批', '已退回']
    status_weights = [0.1, 0.2, 0.3, 0.35, 0.05]
    
    work_contents = [
        '协助客户进行设备搬迁',
        '配合客户进行线路整改',
        '协助客户进行设备调试',
        '配合客户进行系统升级',
        '协助客户进行现场勘察'
    ]
    
    for i, project in enumerate(projects):
        if project.project_id.startswith('TEST'):
            continue
            
        for j in range(2):
            seq = j + 1
            start_date = today - timedelta(days=j*12)
            end_date = start_date + timedelta(days=5)
            work_id = generate_work_order_no('YG', project.project_id, start_date, seq)
            
            existing = db.query(SpotWork).filter(
                SpotWork.work_id == work_id
            ).first()
            if existing:
                continue
            
            plan = random.choice(spot_plans) if spot_plans else None
            worker = random.choice(workers)
            
            status = random.choices(statuses, weights=status_weights)[0]
            
            spot_work = SpotWork(
                work_id=work_id,
                plan_id=plan.plan_id if plan else None,
                project_id=project.project_id,
                project_name=project.project_name,
                plan_start_date=datetime.combine(start_date, datetime.min.time()),
                plan_end_date=datetime.combine(end_date, datetime.min.time()),
                client_name=project.client_name,
                client_contact=project.client_contact,
                client_contact_info=project.client_contact_info,
                maintenance_personnel=worker.name,
                work_content=random.choice(work_contents) if status != '未进行' else None,
                photos='[]',
                signature='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==' if status == '已审批' else None,
                status=status,
                remarks='工作已完成' if status == '已审批' else None,
                actual_completion_date=datetime.combine(end_date, datetime.min.time()) if status == '已审批' else None
            )
            db.add(spot_work)
            db.flush()
            created_count += 1
            
            if status in ['已提交', '已审批']:
                for k in range(random.randint(2, 4)):
                    spot_worker = SpotWorkWorker(
                        spot_work_id=spot_work.id,
                        project_id=project.project_id,
                        project_name=project.project_name,
                        start_date=datetime.combine(start_date, datetime.min.time()),
                        end_date=datetime.combine(end_date, datetime.min.time()),
                        name=f"工人{k+1}",
                        gender=random.choice(['男', '女']),
                        birth_date=f"{random.randint(1970, 2000)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                        address=f"测试地址{k+1}",
                        id_card_number=f"{random.randint(110000, 659999)}{random.randint(1970, 2000)}{random.randint(1,12):02d}{random.randint(1,28):02d}{random.randint(1000, 9999)}",
                        issuing_authority="测试公安局",
                        valid_period=f"{random.randint(2020, 2030)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                        id_card_front="",
                        id_card_back=""
                    )
                    db.add(spot_worker)
                    worker_count += 1
            
            create_operation_log(db, 'spot_work', spot_work.id, spot_work.work_id,
                               worker, 'CREATE', '创建零星用工工单')
            
            if status in ['已提交', '已审批', '已退回']:
                create_operation_log(db, 'spot_work', spot_work.id, spot_work.work_id,
                                   worker, 'SUBMIT', '提交零星用工工单')
            
            if status == '已审批':
                manager = random.choice([p for p in personnels if p.role in ['管理员', '部门经理']] or personnels)
                create_operation_log(db, 'spot_work', spot_work.id, spot_work.work_id,
                                   manager, 'APPROVE', '审批通过零星用工工单')
            
            if status == '已退回':
                manager = random.choice([p for p in personnels if p.role in ['管理员', '部门经理']] or personnels)
                create_operation_log(db, 'spot_work', spot_work.id, spot_work.work_id,
                                   manager, 'REJECT', '退回零星用工工单，需要补充工作内容')
    
    db.commit()
    print(f"零星用工工单数据创建完成，新增 {created_count} 条工单，{worker_count} 条施工人员记录")
    return created_count

def create_operation_log(db, work_order_type, work_order_id, work_order_no, operator, operation_code, remark):
    """
    创建工单操作日志
    """
    operation_names = {
        'CREATE': '创建',
        'SUBMIT': '提交',
        'APPROVE': '审批通过',
        'REJECT': '退回',
        'MODIFY': '修改',
        'DELETE': '删除',
        'ISSUE': '下发',
        'COMPLETE': '完成'
    }
    
    operation_type_name = operation_names.get(operation_code, operation_code)
    
    from sqlalchemy import text
    conn = db.connection()
    conn.execute(text("""
        INSERT INTO work_order_operation_log 
        (work_order_type, work_order_id, work_order_no, operator_name, operator_id, 
         operation_type, operation_type_code, operation_type_name, operation_remark, created_at)
        VALUES 
        (:work_order_type, :work_order_id, :work_order_no, :operator_name, :operator_id, 
         :operation_type, :operation_type_code, :operation_type_name, :operation_remark, NOW())
    """), {
        'work_order_type': work_order_type,
        'work_order_id': work_order_id,
        'work_order_no': work_order_no,
        'operator_name': operator.name,
        'operator_id': operator.id,
        'operation_type': operation_type_name,
        'operation_type_code': operation_code,
        'operation_type_name': operation_type_name,
        'operation_remark': remark
    })

def create_spare_parts_inbound(db, spare_parts, personnels):
    """
    创建备品备件入库记录
    """
    print("正在创建备品备件入库记录...")
    created_count = 0
    today = datetime.now().date()
    
    workers = [p for p in personnels if p.role in ['运维人员', '材料员']]
    if not workers:
        workers = personnels
    
    for i, part in enumerate(spare_parts):
        for j in range(2):
            inbound_date = today - timedelta(days=j*30 + i*5)
            inbound_no = f"RK-{inbound_date.strftime('%Y%m%d')}-{i:03d}{j:02d}"
            
            existing = db.query(SparePartsInbound).filter(
                SparePartsInbound.inbound_no == inbound_no
            ).first()
            if existing:
                continue
            
            worker = random.choice(workers)
            
            inbound = SparePartsInbound(
                inbound_no=inbound_no,
                product_name=part.product_name,
                brand=part.brand,
                model=part.model,
                quantity=random.randint(5, 20),
                supplier=f"供应商{random.randint(1, 5)}",
                unit=part.unit,
                user_name=worker.name,
                remarks='常规采购入库'
            )
            db.add(inbound)
            created_count += 1
    
    db.commit()
    print(f"备品备件入库记录创建完成，新增 {created_count} 条")
    return created_count

def create_spare_parts_usage(db, spare_parts, projects, personnels):
    """
    创建备品备件领用记录
    """
    print("正在创建备品备件领用记录...")
    created_count = 0
    today = datetime.now().date()
    
    workers = [p for p in personnels if p.role == '运维人员']
    if not workers:
        workers = personnels
    
    valid_projects = [p for p in projects if not p.project_id.startswith('TEST')]
    
    for i, part in enumerate(spare_parts[:5]):
        for j in range(2):
            usage_date = today - timedelta(days=j*15 + i*3)
            
            worker = random.choice(workers)
            project = random.choice(valid_projects) if valid_projects else None
            
            usage = SparePartsUsage(
                product_name=part.product_name,
                brand=part.brand,
                model=part.model,
                quantity=random.randint(1, 3),
                user_name=worker.name,
                issue_time=datetime.combine(usage_date, datetime.min.time()),
                unit=part.unit,
                project_id=project.project_id if project else None,
                project_name=project.project_name if project else None,
                stock_id=part.id,
                status='已使用'
            )
            db.add(usage)
            created_count += 1
    
    db.commit()
    print(f"备品备件领用记录创建完成，新增 {created_count} 条")
    return created_count

def create_repair_tools_inbound(db, tools, personnels):
    """
    创建维修工具入库记录
    """
    print("正在创建维修工具入库记录...")
    created_count = 0
    today = datetime.now().date()
    
    workers = [p for p in personnels if p.role in ['运维人员', '材料员']]
    if not workers:
        workers = personnels
    
    for i, tool in enumerate(tools):
        inbound_date = today - timedelta(days=i*20)
        inbound_no = f"GJRK-{inbound_date.strftime('%Y%m%d')}-{i:03d}"
        
        existing = db.query(RepairToolsInbound).filter(
            RepairToolsInbound.inbound_no == inbound_no
        ).first()
        if existing:
            continue
        
        worker = random.choice(workers)
        
        inbound = RepairToolsInbound(
            inbound_no=inbound_no,
            tool_name=tool.tool_name,
            tool_id=tool.tool_id,
            category=tool.category,
            specification=tool.specification,
            quantity=random.randint(2, 5),
            unit=tool.unit,
            supplier=f"工具供应商{random.randint(1, 3)}",
            location=tool.location,
            user_name=worker.name,
            remark='常规采购入库'
        )
        db.add(inbound)
        created_count += 1
    
    db.commit()
    print(f"维修工具入库记录创建完成，新增 {created_count} 条")
    return created_count

def create_repair_tools_issue(db, tools, projects, personnels):
    """
    创建维修工具领用记录
    """
    print("正在创建维修工具领用记录...")
    created_count = 0
    today = datetime.now().date()
    
    workers = [p for p in personnels if p.role == '运维人员']
    if not workers:
        workers = personnels
    
    valid_projects = [p for p in projects if not p.project_id.startswith('TEST')]
    
    for i, tool in enumerate(tools[:4]):
        for j in range(2):
            issue_date = today - timedelta(days=j*20 + i*5)
            
            worker = random.choice(workers)
            project = random.choice(valid_projects) if valid_projects else None
            
            is_returned = j == 0
            
            issue = RepairToolsIssue(
                tool_id=tool.tool_id,
                tool_name=tool.tool_name,
                specification=tool.specification,
                quantity=1,
                return_quantity=1 if is_returned else 0,
                user_id=worker.id,
                user_name=worker.name,
                issue_time=datetime.combine(issue_date, datetime.min.time()),
                return_time=datetime.combine(issue_date + timedelta(days=3), datetime.min.time()) if is_returned else None,
                project_id=project.project_id if project else None,
                project_name=project.project_name if project else None,
                status='已归还' if is_returned else '已领用',
                stock_id=tool.id
            )
            db.add(issue)
            created_count += 1
    
    db.commit()
    print(f"维修工具领用记录创建完成，新增 {created_count} 条")
    return created_count

def main():
    """
    主函数：生成全流程测试数据
    """
    print("=" * 60)
    print("开始生成全流程测试数据")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        projects = db.query(ProjectInfo).filter(
            ~ProjectInfo.project_id.startswith('TEST')
        ).all()
        print(f"\n找到 {len(projects)} 个有效项目")
        
        personnels = db.query(Personnel).all()
        print(f"找到 {len(personnels)} 个人员")
        
        operation_types = create_operation_types(db)
        
        inspection_items = create_inspection_items(db)
        
        spare_parts = create_spare_parts(db)
        
        tools = create_repair_tools(db)
        
        plans = create_maintenance_plans(db, projects, personnels)
        
        create_periodic_inspections(db, projects, plans, personnels, inspection_items)
        
        create_temporary_repairs(db, projects, plans, personnels)
        
        create_spot_works(db, projects, plans, personnels)
        
        create_spare_parts_inbound(db, spare_parts, personnels)
        
        create_spare_parts_usage(db, spare_parts, projects, personnels)
        
        create_repair_tools_inbound(db, tools, personnels)
        
        create_repair_tools_issue(db, tools, projects, personnels)
        
        print("\n" + "=" * 60)
        print("全流程测试数据生成完成！")
        print("=" * 60)
        
        print("\n数据统计：")
        print(f"- 维保计划: {db.query(MaintenancePlan).count()} 条")
        print(f"- 定期巡检工单: {db.query(PeriodicInspection).count()} 条")
        print(f"- 定期巡检记录: {db.query(PeriodicInspectionRecord).count()} 条")
        print(f"- 临时维修工单: {db.query(TemporaryRepair).count()} 条")
        print(f"- 零星用工工单: {db.query(SpotWork).count()} 条")
        print(f"- 施工人员记录: {db.query(SpotWorkWorker).count()} 条")
        print(f"- 备品备件库存: {db.query(SparePartsStock).count()} 条")
        print(f"- 备品备件入库: {db.query(SparePartsInbound).count()} 条")
        print(f"- 备品备件领用: {db.query(SparePartsUsage).count()} 条")
        print(f"- 维修工具库存: {db.query(RepairToolsStock).count()} 条")
        print(f"- 维修工具入库: {db.query(RepairToolsInbound).count()} 条")
        print(f"- 维修工具领用: {db.query(RepairToolsIssue).count()} 条")
        print(f"- 操作类型: {db.query(OperationType).count()} 条")
        print(f"- 巡检事项: {db.query(InspectionItem).count()} 条")
        print(f"- 操作日志: {db.query(WorkOrderOperationLog).count()} 条")
        
    except Exception as e:
        print(f"生成数据时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    main()
