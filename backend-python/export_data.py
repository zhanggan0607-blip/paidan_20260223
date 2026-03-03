"""
数据库数据同步脚本
从本地数据库导出数据并同步到服务器数据库
"""
import json
import subprocess
import sys
from datetime import datetime
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

LOCAL_DB_URL = "postgresql://postgres:123456@localhost:5432/tq?client_encoding=utf8"

TABLES_TO_SYNC = [
    "customer",
    "dictionary",
    "inspection_item",
    "maintenance_log",
    "maintenance_plan",
    "online_users",
    "operation_type",
    "periodic_inspection",
    "periodic_inspection_record",
    "personnel",
    "project_info",
    "repair_tools_inbound",
    "repair_tools_issue",
    "repair_tools_stock",
    "spare_parts_inbound",
    "spare_parts_stock",
    "spare_parts_usage",
    "spot_work",
    "spot_work_worker",
    "temporary_repair",
    "user_dashboard_config",
    "weekly_report",
    "work_order_operation_log",
    "work_plan",
]


def export_local_data():
    """导出本地数据库数据"""
    print("正在连接本地数据库...")
    engine = create_engine(LOCAL_DB_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    all_data = {}
    inspector = inspect(engine)
    
    for table in TABLES_TO_SYNC:
        try:
            if table not in inspector.get_table_names():
                print(f"  表 {table} 不存在，跳过")
                continue
            
            result = session.execute(text(f'SELECT * FROM "{table}"'))
            columns = result.keys()
            rows = result.fetchall()
            
            data = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    if hasattr(value, 'isoformat'):
                        value = value.isoformat()
                    row_dict[col] = value
                data.append(row_dict)
            
            all_data[table] = {
                "columns": list(columns),
                "data": data
            }
            print(f"  导出 {table}: {len(data)} 条记录")
        except Exception as e:
            print(f"  导出 {table} 失败: {e}")
    
    session.close()
    engine.dispose()
    return all_data


def save_to_file(data, filename="db_export.json"):
    """保存数据到文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n数据已保存到 {filename}")
    return filename


if __name__ == "__main__":
    print("=" * 50)
    print("本地数据库数据导出")
    print("=" * 50)
    
    data = export_local_data()
    
    total_records = sum(len(d["data"]) for d in data.values())
    print(f"\n总计导出 {len(data)} 个表，{total_records} 条记录")
    
    filename = save_to_file(data)
    print(f"\n请将 {filename} 上传到服务器后运行导入脚本")
