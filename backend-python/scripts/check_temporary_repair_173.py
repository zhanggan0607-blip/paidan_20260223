"""
检查 temporary_repair 表中 ID 173 的记录
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text

ALIYUN_RDS_URL = "postgresql://postgres:Lily421020%23@pgm-uf6cml154nbjz51y6o.pg.rds.aliyuncs.com:5432/sstcp"

engine = create_engine(ALIYUN_RDS_URL)

with engine.connect() as conn:
    print('=' * 60)
    print('检查 temporary_repair 表中 ID 173 的记录')
    print('=' * 60)
    
    result = conn.execute(text("""
        SELECT id, repair_id, project_name, status, is_deleted, created_at, updated_at, actual_completion_date
        FROM temporary_repair 
        WHERE id = 173
    """))
    row = result.fetchone()
    
    if row:
        print(f"ID: {row[0]}")
        print(f"repair_id: {row[1]}")
        print(f"project_name: {row[2]}")
        print(f"status: {row[3]}")
        print(f"is_deleted: {row[4]}")
        print(f"created_at: {row[5]}")
        print(f"updated_at: {row[6]}")
        print(f"actual_completion_date: {row[7]}")
    else:
        print("ID 173 的记录不存在")
    
    print()
    print('=' * 60)
    print("检查工单编号 WX-TQ-2025-001A-SH-20260310-0020 的记录")
    print('=' * 60)
    
    result = conn.execute(text("""
        SELECT id, repair_id, project_name, status, is_deleted, created_at, updated_at, actual_completion_date
        FROM temporary_repair 
        WHERE repair_id = 'WX-TQ-2025-001A-SH-20260310-0020'
    """))
    row = result.fetchone()
    
    if row:
        print(f"ID: {row[0]}")
        print(f"repair_id: {row[1]}")
        print(f"project_name: {row[2]}")
        print(f"status: {row[3]}")
        print(f"is_deleted: {row[4]}")
        print(f"created_at: {row[5]}")
        print(f"updated_at: {row[6]}")
        print(f"actual_completion_date: {row[7]}")
    else:
        print("工单编号 WX-TQ-2025-001A-SH-20260310-0020 的记录不存在")
    
    print()
    print('=' * 60)
    print("检查本年已完成的临时维修工单（前10条）")
    print('=' * 60)
    
    result = conn.execute(text("""
        SELECT id, repair_id, project_name, status, is_deleted, actual_completion_date
        FROM temporary_repair 
        WHERE status = '已完成' 
        AND EXTRACT(YEAR FROM actual_completion_date) = 2026
        AND is_deleted = false
        ORDER BY actual_completion_date DESC
        LIMIT 10
    """))
    
    for row in result:
        print(f"ID: {row[0]}, repair_id: {row[1]}, status: {row[3]}, is_deleted: {row[4]}")
