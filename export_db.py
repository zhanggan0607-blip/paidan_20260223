"""
导出本机PostgreSQL数据库数据到JSON文件
"""
import json
import psycopg2
from datetime import datetime

def export_database():
    conn = psycopg2.connect(
        host="localhost",
        database="tq",
        user="postgres",
        password="123456",
        port=5432
    )
    
    tables = [
        'customer', 'dictionary', 'inspection_item', 'maintenance_log',
        'maintenance_plan', 'operation_type', 'periodic_inspection',
        'periodic_inspection_record', 'personnel', 'project_info',
        'repair_tools_inbound', 'repair_tools_issue', 'repair_tools_stock',
        'spare_parts_inbound', 'spare_parts_stock', 'spare_parts_usage',
        'spot_work', 'spot_work_worker', 'temporary_repair',
        'user_dashboard_config', 'weekly_report', 'work_order_operation_log',
        'work_plan'
    ]
    
    data = {}
    for table in tables:
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table}")
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            data[table] = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    val = row[i]
                    if isinstance(val, datetime):
                        val = val.isoformat()
                    row_dict[col] = val
                data[table].append(row_dict)
            print(f"导出 {table}: {len(rows)} 条记录")
            cursor.close()
        except Exception as e:
            print(f"导出 {table} 失败: {e}")
            data[table] = []
    
    conn.close()
    
    with open("D:\\共享文件\\SSTCP-paidan260120\\db_export.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n数据已导出到 db_export.json")

if __name__ == "__main__":
    export_database()
