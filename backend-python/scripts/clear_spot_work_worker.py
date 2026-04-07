"""
清除服务器数据库（阿里云RDS）中的施工人员数据
清除 spot_work_worker 表的所有数据
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


def clear_spot_work_worker():
    """
    清除施工人员表的数据
    spot_work_worker 表没有 is_deleted 字段，使用物理删除
    """
    table_name = "spot_work_worker"
    table_desc = "施工人员信息"

    print("\n" + "=" * 60)
    print(f"警告: 此操作将清除阿里云RDS数据库中 {table_desc} 的所有数据")
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
        
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count_before = cursor.fetchone()[0]
        print(f"  {table_desc}({table_name}): {count_before} 条")
        
        if count_before == 0:
            print("\n表已经是空的，无需清理。")
            return
        
        print("\n" + "-" * 60)
        print("开始清理数据...")
        print("-" * 60)
        
        cursor.execute(f"DELETE FROM {table_name}")
        affected = cursor.rowcount
        print(f"  [已删除] {table_desc}({table_name}): {affected} 条记录")
        
        conn.commit()
        
        print("\n" + "-" * 60)
        print("清理后验证:")
        print("-" * 60)
        
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count_after = cursor.fetchone()[0]
        status = "✓ 已清空" if count_after == 0 else f"✗ 剩余 {count_after} 条"
        print(f"  {table_name}: {status}")
        
        print("\n" + "=" * 60)
        print("施工人员数据清理完成!")
        print("=" * 60)
        
        cursor.close()
    finally:
        conn.close()


if __name__ == "__main__":
    clear_spot_work_worker()
