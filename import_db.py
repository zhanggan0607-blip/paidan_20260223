"""
导入数据到服务器PostgreSQL数据库
"""
import json
import psycopg2
from datetime import datetime

def import_database():
    conn = psycopg2.connect(
        host="localhost",
        database="sstcp_maintenance",
        user="sstcp_user",
        password="Lily421020",
        port=5432
    )
    conn.autocommit = False
    cursor = conn.cursor()
    
    with open("/tmp/db_export.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    table_order = [
        'project_info', 'customer', 'personnel', 'dictionary', 'operation_type',
        'inspection_item', 'maintenance_plan', 'work_plan',
        'periodic_inspection', 'periodic_inspection_record',
        'temporary_repair', 'spot_work', 'spot_work_worker',
        'maintenance_log', 'spare_parts_inbound', 'spare_parts_stock',
        'spare_parts_usage', 'repair_tools_inbound', 'repair_tools_issue',
        'repair_tools_stock', 'weekly_report', 'work_order_operation_log',
        'user_dashboard_config'
    ]
    
    for table in table_order:
        if table not in data or not data[table]:
            print(f"跳过 {table}: 无数据")
            continue
        
        rows = data[table]
        if not rows:
            continue
        
        columns = list(rows[0].keys())
        placeholders = ', '.join(['%s'] * len(columns))
        columns_str = ', '.join(columns)
        
        success_count = 0
        for row in rows:
            values = []
            for col in columns:
                val = row.get(col)
                values.append(val)
            
            try:
                sql = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
                cursor.execute(sql, values)
                success_count += 1
            except Exception as e:
                print(f"插入 {table} 失败: {e}")
                conn.rollback()
                cursor = conn.cursor()
        
        try:
            conn.commit()
            print(f"导入 {table}: {success_count} 条记录")
        except Exception as e:
            print(f"提交 {table} 失败: {e}")
            conn.rollback()
    
    cursor.close()
    conn.close()
    print("\n数据导入完成")

if __name__ == "__main__":
    import_database()
