# -*- coding: utf-8 -*-
"""
批量插入测试数据脚本
为2024、2025、2026年生成随机测试数据
每年40-80条，人员随机，工单类型随机，状态随机
"""

import sys
import os
import random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
from app.models.maintenance_plan import MaintenancePlan

TEST_SUFFIX = "TESTDATA"

PLAN_TYPES = ['定期维保', '临时维修', '零星用工']
PLAN_STATUSES = ['待执行', '执行中', '已完成']
EXECUTION_STATUSES = {
    '待执行': '未开始',
    '执行中': '进行中',
    '已完成': '已完成'
}

def get_db_session():
    settings = get_settings()
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    return Session(), engine

def get_existing_projects(session):
    result = session.execute(text("SELECT project_id, project_name, client_name FROM project_info"))
    return [dict(row._mapping) for row in result]

def get_personnel(session):
    result = session.execute(text("SELECT name, phone, department FROM personnel ORDER BY id"))
    return [dict(row._mapping) for row in result]

def generate_plan_id(plan_type, project_id, date, seq):
    prefix_map = {
        '定期维保': 'XJ',
        '临时维修': 'WX',
        '零星用工': 'YG'
    }
    prefix = prefix_map[plan_type]
    return f"{prefix}-{project_id}-{date.strftime('%Y%m%d')}-{seq:03d}-{TEST_SUFFIX}"

def generate_data_for_year(year, projects, personnel):
    test_data = []
    count = random.randint(40, 80)
    
    print(f"\n生成 {year} 年数据: {count} 条")
    
    for i in range(count):
        project = random.choice(projects)
        person = random.choice(personnel)
        plan_type = random.choice(PLAN_TYPES)
        plan_status = random.choices(
            PLAN_STATUSES,
            weights=[0.3, 0.2, 0.5],
            k=1
        )[0]
        exec_status = EXECUTION_STATUSES[plan_status]
        
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        try:
            plan_start = datetime(year, month, day)
        except:
            plan_start = datetime(year, month, 1)
        
        duration = random.randint(1, 7)
        plan_end = plan_start + timedelta(days=duration)
        
        if plan_status == '已完成':
            execution_date = plan_start + timedelta(days=random.randint(0, duration))
        elif plan_status == '执行中':
            execution_date = None
        else:
            execution_date = None
        
        completion_rate = 100 if plan_status == '已完成' else (random.randint(30, 70) if plan_status == '执行中' else 0)
        
        plan_id = generate_plan_id(plan_type, project['project_id'], plan_start, i+1)
        
        equipment_names = {
            '定期维保': ['巡检设备', '监控设备', '网络设备', '服务器', 'UPS电源', '空调设备'],
            '临时维修': ['维修设备', '故障设备', '报修设备', '损坏设备'],
            '零星用工': ['用工项目', '辅助作业', '现场支持', '临时任务']
        }
        
        equipment_name = f"{random.choice(equipment_names[plan_type])}{i+1}-{TEST_SUFFIX}"
        
        data = MaintenancePlan(
            plan_id=plan_id,
            plan_name=f"{plan_type}-{project['project_name']}-{year}{month:02d}-{i+1}-{TEST_SUFFIX}",
            project_id=project['project_id'],
            plan_type=plan_type,
            equipment_id=f"EQ-{plan_type[:2]}-{year}{i+1:04d}",
            equipment_name=equipment_name,
            equipment_model=f"MODEL-{year}-{i+1:04d}",
            equipment_location=f"{project['project_name']} {random.randint(1,10)}楼机房",
            plan_start_date=plan_start,
            plan_end_date=plan_end,
            execution_date=execution_date,
            next_maintenance_date=plan_end + timedelta(days=random.randint(30, 90)) if plan_status == '已完成' and plan_type == '定期维保' else None,
            responsible_person=person['name'],
            responsible_department=person['department'] or "维保部",
            contact_info=person['phone'],
            maintenance_content=f"{plan_type}内容{i+1}: 详细作业内容-{TEST_SUFFIX}",
            maintenance_requirements="按要求执行",
            maintenance_standard="符合标准",
            plan_status=plan_status,
            execution_status=exec_status,
            completion_rate=completion_rate,
            remarks=f"测试数据-{plan_type}-{year}年-{TEST_SUFFIX}"
        )
        test_data.append(data)
    
    return test_data

def delete_old_test_data(session):
    result = session.execute(
        text("DELETE FROM maintenance_plan WHERE remarks LIKE :suffix"),
        {"suffix": f"%{TEST_SUFFIX}%"}
    )
    return result.rowcount

def main():
    print("=" * 60)
    print("批量插入测试数据")
    print(f"测试数据后缀代号: {TEST_SUFFIX}")
    print("=" * 60)
    
    session, engine = get_db_session()
    
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
        
        print("\n" + "-" * 60)
        deleted_count = delete_old_test_data(session)
        print(f"删除旧测试数据: {deleted_count} 条")
        
        all_data = []
        for year in [2024, 2025, 2026]:
            year_data = generate_data_for_year(year, projects, personnel)
            all_data.extend(year_data)
            print(f"  {year}年: {len(year_data)} 条")
        
        print("\n插入数据...")
        for data in all_data:
            session.add(data)
        
        session.commit()
        
        print("\n" + "=" * 60)
        print("测试数据插入成功!")
        print(f"  总计: {len(all_data)} 条")
        print("=" * 60)
        
        print("\n按年份统计:")
        result = session.execute(text("""
            SELECT 
                EXTRACT(YEAR FROM plan_end_date)::int as year,
                plan_type,
                plan_status,
                COUNT(*) as cnt
            FROM maintenance_plan 
            WHERE remarks LIKE :suffix
            GROUP BY year, plan_type, plan_status
            ORDER BY year, plan_type, plan_status
        """), {"suffix": f"%{TEST_SUFFIX}%"})
        
        current_year = None
        for row in result:
            if current_year != row.year:
                current_year = row.year
                print(f"\n  {row.year}年:")
            print(f"    {row.plan_type} | {row.plan_status}: {row.cnt} 条")
        
        print("\n\n按负责人统计:")
        result = session.execute(text("""
            SELECT 
                responsible_person,
                COUNT(*) as cnt
            FROM maintenance_plan 
            WHERE remarks LIKE :suffix
            GROUP BY responsible_person
            ORDER BY cnt DESC
        """), {"suffix": f"%{TEST_SUFFIX}%"})
        
        for row in result:
            print(f"  {row.responsible_person}: {row.cnt} 条")
        
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
