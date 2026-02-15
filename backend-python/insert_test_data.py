# -*- coding: utf-8 -*-
"""
批量插入测试数据脚本
为2024、2025、2026年生成随机测试数据
每年40-80条，人员随机，工单类型随机，状态随机
数据分配到三种工单表：定期巡检单、临时维修单、零星用工单
"""

import sys
import os
import random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
from app.models.periodic_inspection import PeriodicInspection
from app.models.temporary_repair import TemporaryRepair
from app.models.spot_work import SpotWork

TEST_SUFFIX = "TESTDATA"

WORK_ORDER_TYPES = ['定期巡检', '临时维修', '零星用工']
STATUSES = ['待执行', '执行中', '已完成']

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

def generate_work_order_id(work_order_type, project_id, date, seq):
    prefix_map = {
        '定期巡检': 'XJ',
        '临时维修': 'WX',
        '零星用工': 'YG'
    }
    prefix = prefix_map[work_order_type]
    return f"{prefix}-{project_id}-{date.strftime('%Y%m%d')}-{seq:03d}-{TEST_SUFFIX}"

def generate_data_for_year(year, projects, personnel):
    periodic_data = []
    repair_data = []
    spot_work_data = []
    
    count = random.randint(40, 80)
    
    print(f"\n生成 {year} 年数据: {count} 条")
    
    for i in range(count):
        project = random.choice(projects)
        person = random.choice(personnel)
        work_order_type = random.choice(WORK_ORDER_TYPES)
        
        status = random.choices(
            STATUSES,
            weights=[0.3, 0.2, 0.5],
            k=1
        )[0]
        
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        try:
            plan_start = datetime(year, month, day)
        except:
            plan_start = datetime(year, month, 1)
        
        duration = random.randint(1, 7)
        plan_end = plan_start + timedelta(days=duration)
        
        work_order_id = generate_work_order_id(work_order_type, project['project_id'], plan_start, i+1)
        
        remarks = f"测试数据-{work_order_type}-{year}年-{TEST_SUFFIX}"
        
        if work_order_type == '定期巡检':
            data = PeriodicInspection(
                inspection_id=work_order_id,
                project_id=project['project_id'],
                project_name=project['project_name'],
                plan_start_date=plan_start,
                plan_end_date=plan_end,
                client_name=project.get('client_name', ''),
                maintenance_personnel=person['name'],
                status=status,
                remarks=remarks
            )
            periodic_data.append(data)
        elif work_order_type == '临时维修':
            data = TemporaryRepair(
                repair_id=work_order_id,
                project_id=project['project_id'],
                project_name=project['project_name'],
                plan_start_date=plan_start,
                plan_end_date=plan_end,
                client_name=project.get('client_name', ''),
                maintenance_personnel=person['name'],
                status=status,
                remarks=remarks
            )
            repair_data.append(data)
        else:
            data = SpotWork(
                work_id=work_order_id,
                project_id=project['project_id'],
                project_name=project['project_name'],
                plan_start_date=plan_start,
                plan_end_date=plan_end,
                client_name=project.get('client_name', ''),
                maintenance_personnel=person['name'],
                status=status,
                remarks=remarks
            )
            spot_work_data.append(data)
    
    return periodic_data, repair_data, spot_work_data

def generate_delayed_data_for_year(year, projects, personnel):
    """生成延期完成的工单数据 - execution_date > plan_end_date"""
    periodic_data = []
    repair_data = []
    spot_work_data = []
    
    count = random.randint(10, 30)
    
    print(f"\n生成 {year} 年延期完成数据: {count} 条")
    
    for i in range(count):
        project = random.choice(projects)
        person = random.choice(personnel)
        work_order_type = random.choice(WORK_ORDER_TYPES)
        
        month = random.randint(1, 12)
        day = random.randint(1, 25)
        try:
            plan_start = datetime(year, month, day)
        except:
            plan_start = datetime(year, month, 1)
        
        duration = random.randint(1, 5)
        plan_end = plan_start + timedelta(days=duration)
        
        work_order_id = generate_work_order_id(work_order_type, project['project_id'], plan_start, 900 + i)
        
        remarks = f"测试数据-延期完成-{work_order_type}-{year}年-{TEST_SUFFIX}"
        
        if work_order_type == '定期巡检':
            data = PeriodicInspection(
                inspection_id=work_order_id,
                project_id=project['project_id'],
                project_name=project['project_name'],
                plan_start_date=plan_start,
                plan_end_date=plan_end,
                client_name=project.get('client_name', ''),
                maintenance_personnel=person['name'],
                status='已完成',
                remarks=remarks
            )
            periodic_data.append(data)
        elif work_order_type == '临时维修':
            data = TemporaryRepair(
                repair_id=work_order_id,
                project_id=project['project_id'],
                project_name=project['project_name'],
                plan_start_date=plan_start,
                plan_end_date=plan_end,
                client_name=project.get('client_name', ''),
                maintenance_personnel=person['name'],
                status='已完成',
                remarks=remarks
            )
            repair_data.append(data)
        else:
            data = SpotWork(
                work_id=work_order_id,
                project_id=project['project_id'],
                project_name=project['project_name'],
                plan_start_date=plan_start,
                plan_end_date=plan_end,
                client_name=project.get('client_name', ''),
                maintenance_personnel=person['name'],
                status='已完成',
                remarks=remarks
            )
            spot_work_data.append(data)
    
    return periodic_data, repair_data, spot_work_data

def delete_old_test_data(session):
    suffix_pattern = f"%{TEST_SUFFIX}%"
    
    periodic_count = session.execute(
        text("DELETE FROM periodic_inspection WHERE remarks LIKE :suffix"),
        {"suffix": suffix_pattern}
    ).rowcount
    
    repair_count = session.execute(
        text("DELETE FROM temporary_repair WHERE remarks LIKE :suffix"),
        {"suffix": suffix_pattern}
    ).rowcount
    
    spot_work_count = session.execute(
        text("DELETE FROM spot_work WHERE remarks LIKE :suffix"),
        {"suffix": suffix_pattern}
    ).rowcount
    
    return periodic_count, repair_count, spot_work_count

def main():
    print("=" * 60)
    print("批量插入测试数据")
    print(f"测试数据后缀代号: {TEST_SUFFIX}")
    print("数据分配到三种工单表：定期巡检单、临时维修单、零星用工单")
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
        periodic_count, repair_count, spot_work_count = delete_old_test_data(session)
        print(f"删除旧测试数据:")
        print(f"  定期巡检单: {periodic_count} 条")
        print(f"  临时维修单: {repair_count} 条")
        print(f"  零星用工单: {spot_work_count} 条")
        
        all_periodic = []
        all_repair = []
        all_spot_work = []
        
        for year in [2024, 2025, 2026]:
            periodic_data, repair_data, spot_work_data = generate_data_for_year(year, projects, personnel)
            delayed_periodic, delayed_repair, delayed_spot_work = generate_delayed_data_for_year(year, projects, personnel)
            
            all_periodic.extend(periodic_data)
            all_periodic.extend(delayed_periodic)
            all_repair.extend(repair_data)
            all_repair.extend(delayed_repair)
            all_spot_work.extend(spot_work_data)
            all_spot_work.extend(delayed_spot_work)
            
            total_normal = len(periodic_data) + len(repair_data) + len(spot_work_data)
            total_delayed = len(delayed_periodic) + len(delayed_repair) + len(delayed_spot_work)
            print(f"  {year}年: {total_normal} 条正常 + {total_delayed} 条延期")
        
        print("\n插入数据...")
        for data in all_periodic:
            session.add(data)
        for data in all_repair:
            session.add(data)
        for data in all_spot_work:
            session.add(data)
        
        session.commit()
        
        total_count = len(all_periodic) + len(all_repair) + len(all_spot_work)
        
        print("\n" + "=" * 60)
        print("测试数据插入成功!")
        print(f"  总计: {total_count} 条")
        print(f"    定期巡检单: {len(all_periodic)} 条")
        print(f"    临时维修单: {len(all_repair)} 条")
        print(f"    零星用工单: {len(all_spot_work)} 条")
        print("=" * 60)
        
        print("\n按年份和类型统计:")
        for table_name, id_field in [('periodic_inspection', 'inspection_id'), 
                                      ('temporary_repair', 'repair_id'), 
                                      ('spot_work', 'work_id')]:
            type_name = {
                'periodic_inspection': '定期巡检单',
                'temporary_repair': '临时维修单',
                'spot_work': '零星用工单'
            }[table_name]
            
            result = session.execute(text(f"""
                SELECT 
                    EXTRACT(YEAR FROM plan_end_date)::int as year,
                    status,
                    COUNT(*) as cnt
                FROM {table_name} 
                WHERE remarks LIKE :suffix
                GROUP BY year, status
                ORDER BY year, status
            """), {"suffix": f"%{TEST_SUFFIX}%"})
            
            print(f"\n  {type_name}:")
            current_year = None
            for row in result:
                if current_year != row.year:
                    current_year = row.year
                    print(f"    {row.year}年:")
                print(f"      {row.status}: {row.cnt} 条")
        
        print("\n\n按负责人统计:")
        for table_name, type_name in [('periodic_inspection', '定期巡检单'), 
                                       ('temporary_repair', '临时维修单'), 
                                       ('spot_work', '零星用工单')]:
            result = session.execute(text(f"""
                SELECT 
                    maintenance_personnel,
                    COUNT(*) as cnt
                FROM {table_name} 
                WHERE remarks LIKE :suffix
                GROUP BY maintenance_personnel
                ORDER BY cnt DESC
                LIMIT 5
            """), {"suffix": f"%{TEST_SUFFIX}%"})
            
            print(f"\n  {type_name} Top5:")
            for row in result:
                print(f"    {row.maintenance_personnel}: {row.cnt} 条")
        
        print("\n\n延期完成统计:")
        for table_name, type_name in [('periodic_inspection', '定期巡检单'), 
                                       ('temporary_repair', '临时维修单'), 
                                       ('spot_work', '零星用工单')]:
            result = session.execute(text(f"""
                SELECT 
                    EXTRACT(YEAR FROM plan_end_date)::int as year,
                    COUNT(*) as cnt
                FROM {table_name} 
                WHERE remarks LIKE :suffix_delayed
                GROUP BY year
                ORDER BY year
            """), {"suffix_delayed": f"%延期完成%{TEST_SUFFIX}%"})
            
            print(f"\n  {type_name}:")
            for row in result:
                print(f"    {row.year}年延期完成: {row.cnt} 条")
        
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
