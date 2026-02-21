"""
检查数据库表结构
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine

tables = [
    'maintenance_plan',
    'periodic_inspection',
    'temporary_repair',
    'spot_work',
    'spot_work_worker',
    'spare_parts_stock',
    'spare_parts_inbound',
    'spare_parts_usage',
    'repair_tools_stock',
    'repair_tools_issue',
    'repair_tools_inbound',
    'work_order_operation_log',
    'operation_type',
    'inspection_item'
]

with engine.connect() as conn:
    for table in tables:
        print(f"\n=== {table} 表结构 ===")
        result = conn.execute(text(f"SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = '{table}' ORDER BY ordinal_position"))
        for row in result:
            nullable = "NULL" if row[2] == "YES" else "NOT NULL"
            print(f"  {row[0]}: {row[1]} {nullable}")
