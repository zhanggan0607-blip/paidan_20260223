# -*- coding: utf-8 -*-
"""
为每个项目生成临时维修单和零星用工单
每个项目随机生成5-16个工单
覆盖已结束的、即将开始的、和已经开始的工单
"""

import sys
import os
import random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
from app.models.temporary_repair import TemporaryRepair
from app.models.spot_work import SpotWork

TEST_SUFFIX = "REALDATA2025"

REPAIR_REMARKS = [
    "设备故障维修",
    "线路检修",
    "设备更换配件",
    "系统异常处理",
    "紧急抢修",
    "设备保养维护",
    "电路故障排除",
    "设备调试校准",
    "管道疏通维修",
    "空调设备维修",
    "监控设备检修",
    "消防设备维护",
    "电梯故障处理",
    "门禁系统维修",
    "照明设备更换",
    "水泵设备维修",
    "配电柜检修",
    "弱电系统维护",
    "网络设备维修",
    "安防设备检修",
]

SPOT_WORK_REMARKS = [
    "日常巡检维护",
    "设备清洁保养",
    "场地整理清洁",
    "绿化养护工作",
    "安全检查工作",
    "设备运行记录",
    "环境监测记录",
    "能耗数据采集",
    "设备状态确认",
    "现场技术支持",
    "设备安装调试",
    "系统升级维护",
    "资料整理归档",
    "客户现场服务",
    "应急响应处理",
    "配合验收工作",
    "设备巡检记录",
    "现场协调工作",
    "培训指导工作",
    "临时支援任务",
]

STATUSES_COMPLETED = ['已完成']
STATUSES_IN_PROGRESS = ['执行中', '待审批']
STATUSES_UPCOMING = ['未进行', '待确认']
STATUSES_ALL = ['未进行', '待确认', '执行中', '待审批', '已完成']

def get_db_session():
    settings = get_settings()
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    return Session(), engine

def get_existing_projects(session):
    result = session.execute(text("""
        SELECT project_id, project_name, client_name, 
               completion_date, maintenance_end_date, project_manager
        FROM project_info 
        ORDER BY project_id
    """))
    return [dict(row._mapping) for row in result]

def get_personnel(session):
    result = session.execute(text("SELECT name FROM personnel ORDER BY id"))
    return [row.name for row in result]

def generate_repair_id(project_id, date, seq):
    return f"WX-{project_id}-{date.strftime('%Y%m%d')}-{seq:03d}"

def generate_work_id(project_id, date, seq):
    return f"YG-{project_id}-{date.strftime('%Y%m%d')}-{seq:03d}"

def generate_work_orders_for_project(project, personnel, today):
    repair_orders = []
    spot_work_orders = []
    
    count = random.randint(5, 16)
    
    project_start = project['completion_date']
    project_end = project['maintenance_end_date']
    
    if isinstance(project_start, str):
        project_start = datetime.fromisoformat(project_start.replace('Z', '+00:00').replace('+00:00', ''))
    if isinstance(project_end, str):
        project_end = datetime.fromisoformat(project_end.replace('Z', '+00:00').replace('+00:00', ''))
    
    total_days = (project_end - project_start).days
    if total_days <= 0:
        total_days = 365
    
    completed_count = int(count * 0.4)
    in_progress_count = int(count * 0.3)
    upcoming_count = count - completed_count - in_progress_count
    
    seq = 1
    
    for i in range(completed_count):
        days_offset = random.randint(0, max(1, (today - project_start).days - 30))
        plan_start = project_start + timedelta(days=days_offset)
        plan_end = plan_start + timedelta(days=random.randint(1, 7))
        
        work_type = random.choice(['repair', 'spot_work'])
        person = random.choice(personnel)
        
        if work_type == 'repair':
            order = TemporaryRepair(
                repair_id=generate_repair_id(project['project_id'], plan_start, seq),
                project_id=project['project_id'],
                project_name=project['project_name'],
                plan_start_date=plan_start,
                plan_end_date=plan_end,
                client_name=project.get('client_name', ''),
                maintenance_personnel=person,
                status='已完成',
                remarks=random.choice(REPAIR_REMARKS)
            )
            repair_orders.append(order)
        else:
            order = SpotWork(
                work_id=generate_work_id(project['project_id'], plan_start, seq),
                project_id=project['project_id'],
                project_name=project['project_name'],
                plan_start_date=plan_start,
                plan_end_date=plan_end,
                client_name=project.get('client_name', ''),
                maintenance_personnel=person,
                status='已完成',
                remarks=random.choice(SPOT_WORK_REMARKS)
            )
            spot_work_orders.append(order)
        seq += 1
    
    for i in range(in_progress_count):
        days_ago = random.randint(0, 10)
        plan_start = today - timedelta(days=days_ago)
        plan_end = plan_start + timedelta(days=random.randint(3, 14))
        
        work_type = random.choice(['repair', 'spot_work'])
        person = random.choice(personnel)
        status = random.choice(STATUSES_IN_PROGRESS)
        
        if work_type == 'repair':
            order = TemporaryRepair(
                repair_id=generate_repair_id(project['project_id'], plan_start, seq),
                project_id=project['project_id'],
                project_name=project['project_name'],
                plan_start_date=plan_start,
                plan_end_date=plan_end,
                client_name=project.get('client_name', ''),
                maintenance_personnel=person,
                status=status,
                remarks=random.choice(REPAIR_REMARKS)
            )
            repair_orders.append(order)
        else:
            order = SpotWork(
                work_id=generate_work_id(project['project_id'], plan_start, seq),
                project_id=project['project_id'],
                project_name=project['project_name'],
                plan_start_date=plan_start,
                plan_end_date=plan_end,
                client_name=project.get('client_name', ''),
                maintenance_personnel=person,
                status=status,
                remarks=random.choice(SPOT_WORK_REMARKS)
            )
            spot_work_orders.append(order)
        seq += 1
    
    for i in range(upcoming_count):
        days_ahead = random.randint(1, 30)
        plan_start = today + timedelta(days=days_ahead)
        plan_end = plan_start + timedelta(days=random.randint(1, 7))
        
        if plan_end > project_end:
            plan_end = project_end
        
        work_type = random.choice(['repair', 'spot_work'])
        person = random.choice(personnel)
        status = random.choice(STATUSES_UPCOMING)
        
        if work_type == 'repair':
            order = TemporaryRepair(
                repair_id=generate_repair_id(project['project_id'], plan_start, seq),
                project_id=project['project_id'],
                project_name=project['project_name'],
                plan_start_date=plan_start,
                plan_end_date=plan_end,
                client_name=project.get('client_name', ''),
                maintenance_personnel=person,
                status=status,
                remarks=random.choice(REPAIR_REMARKS)
            )
            repair_orders.append(order)
        else:
            order = SpotWork(
                work_id=generate_work_id(project['project_id'], plan_start, seq),
                project_id=project['project_id'],
                project_name=project['project_name'],
                plan_start_date=plan_start,
                plan_end_date=plan_end,
                client_name=project.get('client_name', ''),
                maintenance_personnel=person,
                status=status,
                remarks=random.choice(SPOT_WORK_REMARKS)
            )
            spot_work_orders.append(order)
        seq += 1
    
    return repair_orders, spot_work_orders

def delete_old_data(session):
    suffix_pattern = f"%{TEST_SUFFIX}%"
    
    repair_count = session.execute(
        text("DELETE FROM temporary_repair WHERE remarks NOT LIKE :suffix"),
        {"suffix": "%TESTDATA%"}
    ).rowcount
    
    spot_work_count = session.execute(
        text("DELETE FROM spot_work WHERE remarks NOT LIKE :suffix"),
        {"suffix": "%TESTDATA%"}
    ).rowcount
    
    return repair_count, spot_work_count

def main():
    print("=" * 60)
    print("为每个项目生成临时维修单和零星用工单")
    print("每个项目随机生成5-16个工单")
    print("覆盖已结束的、即将开始的、和已经开始的工单")
    print("=" * 60)
    
    session, engine = get_db_session()
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    try:
        projects = get_existing_projects(session)
        if not projects:
            print("错误: 没有找到项目数据")
            return
        
        personnel = get_personnel(session)
        if not personnel:
            print("错误: 没有找到人员数据")
            return
        
        print(f"\n找到 {len(projects)} 个项目")
        print(f"找到 {len(personnel)} 名人员")
        print(f"当前日期: {today.strftime('%Y-%m-%d')}")
        
        print("\n" + "-" * 60)
        repair_count, spot_work_count = delete_old_data(session)
        print(f"删除旧数据:")
        print(f"  临时维修单: {repair_count} 条")
        print(f"  零星用工单: {spot_work_count} 条")
        
        all_repair = []
        all_spot_work = []
        
        print("\n" + "-" * 60)
        print("生成工单数据:")
        
        for project in projects:
            repair_orders, spot_work_orders = generate_work_orders_for_project(
                project, personnel, today
            )
            all_repair.extend(repair_orders)
            all_spot_work.extend(spot_work_orders)
            
            print(f"  项目 {project['project_id']} ({project['project_name'][:20]}...): "
                  f"临时维修 {len(repair_orders)} 条, 零星用工 {len(spot_work_orders)} 条")
        
        print("\n插入数据...")
        for data in all_repair:
            session.add(data)
        for data in all_spot_work:
            session.add(data)
        
        session.commit()
        
        total_count = len(all_repair) + len(all_spot_work)
        
        print("\n" + "=" * 60)
        print("数据生成成功!")
        print(f"  总计: {total_count} 条")
        print(f"    临时维修单: {len(all_repair)} 条")
        print(f"    零星用工单: {len(all_spot_work)} 条")
        print("=" * 60)
        
        print("\n按状态统计:")
        for table_name, type_name, id_field in [
            ('temporary_repair', '临时维修单', 'repair_id'),
            ('spot_work', '零星用工单', 'work_id')
        ]:
            result = session.execute(text(f"""
                SELECT status, COUNT(*) as cnt
                FROM {table_name}
                GROUP BY status
                ORDER BY 
                    CASE status 
                        WHEN '未进行' THEN 1 
                        WHEN '待确认' THEN 2 
                        WHEN '执行中' THEN 3 
                        WHEN '待审批' THEN 4 
                        WHEN '已完成' THEN 5 
                    END
            """))
            
            print(f"\n  {type_name}:")
            for row in result:
                print(f"    {row.status}: {row.cnt} 条")
        
        print("\n按项目统计:")
        for table_name, type_name in [
            ('temporary_repair', '临时维修单'),
            ('spot_work', '零星用工单')
        ]:
            result = session.execute(text(f"""
                SELECT project_id, project_name, COUNT(*) as cnt
                FROM {table_name}
                GROUP BY project_id, project_name
                ORDER BY project_id
            """))
            
            print(f"\n  {type_name}:")
            for row in result:
                name_display = row.project_name[:15] + '...' if len(row.project_name) > 15 else row.project_name
                print(f"    {row.project_id} ({name_display}): {row.cnt} 条")
        
    except Exception as e:
        session.rollback()
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()
        engine.dispose()

if __name__ == "__main__":
    main()
