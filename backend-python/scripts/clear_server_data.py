"""
清除服务器数据库（阿里云RDS）中的数据
清除备品备件、维修工具、临时维修工单、零星用工单的所有数据
"""
import os
import psycopg2
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'

with open(env_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            os.environ[key] = value

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')


def clear_tables():
    """
    清除指定表的数据
    - 有is_deleted字段的表使用软删除
    - 没有is_deleted字段的表使用物理删除
    """
    tables_with_soft_delete = [
        ("spot_work", "零星用工单"),
        ("temporary_repair", "临时维修工单"),
        ("spare_parts_usage", "备品备件领用"),
    ]
    
    tables_with_hard_delete = [
        ("spot_work_worker", "施工人员信息"),
        ("spare_parts_stock", "备品备件库存"),
        ("spare_parts_inbound", "备品备件入库"),
        ("repair_tools_stock", "维修工具库存"),
        ("repair_tools_inbound", "维修工具入库"),
        ("repair_tools_issue", "维修工具领用"),
    ]

    print("\n" + "=" * 60)
    print("警告: 此操作将清除阿里云RDS数据库以下表的所有数据:")
    print("  - 备品备件库存、入库、领用")
    print("  - 维修工具库存、入库、领用")
    print("  - 临时维修工单")
    print("  - 零星用工单及施工人员信息")
    print("=" * 60)

    print(f"\n连接数据库: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    conn = psycopg2.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=int(DB_PORT),
        database=DB_NAME
    )
    
    try:
        cursor = conn.cursor()
        
        print("\n" + "-" * 60)
        print("清理前数据统计:")
        print("-" * 60)
        
        total_before = 0
        
        print("\n软删除表（有is_deleted字段）:")
        for table_name, table_desc in tables_with_soft_delete:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE is_deleted = false OR is_deleted IS NULL")
            count = cursor.fetchone()[0]
            total_before += count
            print(f"  {table_desc}({table_name}): {count} 条")
        
        print("\n物理删除表（无is_deleted字段）:")
        for table_name, table_desc in tables_with_hard_delete:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            total_before += count
            print(f"  {table_desc}({table_name}): {count} 条")
        
        print(f"\n  总计: {total_before} 条")
        
        if total_before == 0:
            print("\n所有表都已经是空的，无需清理。")
            return
        
        print("\n" + "-" * 60)
        print("开始清理数据...")
        print("-" * 60)
        
        print("\n[软删除表处理]")
        for table_name, table_desc in tables_with_soft_delete:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE is_deleted = false OR is_deleted IS NULL")
            count_before = cursor.fetchone()[0]
            
            if count_before > 0:
                cursor.execute(
                    f"UPDATE {table_name} SET is_deleted = true, updated_at = NOW() WHERE is_deleted = false OR is_deleted IS NULL"
                )
                affected = cursor.rowcount
                print(f"  [已软删除] {table_desc}({table_name}): {affected} 条记录")
            else:
                print(f"  [跳过] {table_desc}({table_name}): 无数据")
        
        print("\n[物理删除表处理]")
        for table_name, table_desc in tables_with_hard_delete:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count_before = cursor.fetchone()[0]
            
            if count_before > 0:
                cursor.execute(f"DELETE FROM {table_name}")
                affected = cursor.rowcount
                print(f"  [已删除] {table_desc}({table_name}): {affected} 条记录")
            else:
                print(f"  [跳过] {table_desc}({table_name}): 无数据")
        
        conn.commit()
        
        print("\n" + "-" * 60)
        print("清理后验证:")
        print("-" * 60)
        
        total_after = 0
        
        print("\n软删除表:")
        for table_name, table_desc in tables_with_soft_delete:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE is_deleted = false OR is_deleted IS NULL")
            count = cursor.fetchone()[0]
            total_after += count
            status = "✓ 已清空" if count == 0 else f"✗ 剩余 {count} 条"
            print(f"  {table_name}: {status}")
        
        print("\n物理删除表:")
        for table_name, table_desc in tables_with_hard_delete:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            total_after += count
            status = "✓ 已清空" if count == 0 else f"✗ 剩余 {count} 条"
            print(f"  {table_name}: {status}")
        
        print(f"\n  总计剩余: {total_after} 条")
        print("\n" + "=" * 60)
        print("数据清理完成!")
        print("=" * 60)
        
        cursor.close()
    finally:
        conn.close()


if __name__ == "__main__":
    clear_tables()
