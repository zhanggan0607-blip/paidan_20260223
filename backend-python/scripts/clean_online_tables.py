"""
线上服务器数据库表数据清理脚本
清除备品备件、维修工具、临时维修工单、零星用工单的所有数据
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("正在安装psycopg2...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "psycopg2-binary", "-q"])
    import psycopg2
    from psycopg2 import sql

RDS_DB_HOST = "pgm-uf6cml154nbjz51y.pg.rds.aliyuncs.com"
RDS_DB_PORT = 5432
RDS_DB_NAME = "tq"
RDS_DB_USER = "postgres"
RDS_DB_PASSWORD = "Lily421020#"


def get_connection():
    """获取线上RDS数据库连接"""
    return psycopg2.connect(
        host=RDS_DB_HOST,
        port=RDS_DB_PORT,
        database=RDS_DB_NAME,
        user=RDS_DB_USER,
        password=RDS_DB_PASSWORD
    )


def clean_tables():
    """
    清除指定表的所有数据
    按照外键依赖顺序删除
    """
    tables_to_clean = [
        ("spot_work_worker", "施工人员信息"),
        ("spot_work", "零星用工单"),
        ("temporary_repair", "临时维修工单"),
        ("spare_parts_usage", "备品备件领用"),
        ("spare_parts_inbound", "备品备件入库"),
        ("spare_parts_stock", "备品备件库存"),
        ("repair_tools_issue", "维修工具领用"),
        ("repair_tools_inbound", "维修工具入库"),
        ("repair_tools_stock", "维修工具库存"),
    ]
    
    conn = get_connection()
    conn.autocommit = True
    cur = conn.cursor()
    
    print("=" * 60)
    print(f"连接线上数据库: {RDS_DB_NAME}@{RDS_DB_HOST}")
    print("开始清理数据库表数据...")
    print("=" * 60)
    
    for table_name, table_desc in tables_to_clean:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cur.fetchone()[0]
            
            if count > 0:
                cur.execute(f"DELETE FROM {table_name}")
                print(f"[已清除] {table_desc}({table_name}): {count} 条记录")
            else:
                print(f"[跳过] {table_desc}({table_name}): 无数据")
        except Exception as e:
            print(f"[错误] 清理 {table_desc}({table_name}) 失败: {e}")
    
    print("=" * 60)
    print("数据清理完成!")
    print("=" * 60)
    
    cur.close()
    conn.close()


def verify_clean():
    """
    验证数据是否已清除
    """
    tables_to_verify = [
        "spot_work_worker",
        "spot_work",
        "temporary_repair",
        "spare_parts_usage",
        "spare_parts_inbound",
        "spare_parts_stock",
        "repair_tools_issue",
        "repair_tools_inbound",
        "repair_tools_stock",
    ]
    
    conn = get_connection()
    cur = conn.cursor()
    
    print("\n验证清理结果:")
    print("-" * 40)
    all_clean = True
    for table_name in tables_to_verify:
        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cur.fetchone()[0]
        status = "✓ 已清空" if count == 0 else f"✗ 剩余 {count} 条"
        print(f"{table_name}: {status}")
        if count > 0:
            all_clean = False
    print("-" * 40)
    
    cur.close()
    conn.close()
    return all_clean


def main():
    """
    主函数
    """
    print("\n" + "=" * 60)
    print("警告: 此操作将清除线上服务器数据库以下表的所有数据:")
    print(f"  数据库: {RDS_DB_NAME}@{RDS_DB_HOST}")
    print("  - 备品备件库存、入库、领用")
    print("  - 维修工具库存、入库、领用")
    print("  - 临时维修工单")
    print("  - 零星用工单及施工人员信息")
    print("=" * 60)
    
    confirm = input("\n请输入 'YES' 确认执行清理: ")
    
    if confirm != "YES":
        print("操作已取消")
        return
    
    clean_tables()
    verify_clean()


if __name__ == "__main__":
    main()
