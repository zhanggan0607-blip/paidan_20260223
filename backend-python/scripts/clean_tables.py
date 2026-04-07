"""
数据库表数据清理脚本
清除备品备件、维修工具、临时维修工单、零星用工单的所有数据
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine


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
    
    with engine.begin() as conn:
        print("=" * 60)
        print("开始清理数据库表数据...")
        print("=" * 60)
        
        for table_name, table_desc in tables_to_clean:
            try:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                
                if count > 0:
                    conn.execute(text(f"DELETE FROM {table_name}"))
                    print(f"[已清除] {table_desc}({table_name}): {count} 条记录")
                else:
                    print(f"[跳过] {table_desc}({table_name}): 无数据")
            except Exception as e:
                print(f"[错误] 清理 {table_desc}({table_name}) 失败: {e}")
        
        print("=" * 60)
        print("数据清理完成!")
        print("=" * 60)


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
    
    with engine.begin() as conn:
        print("\n验证清理结果:")
        print("-" * 40)
        all_clean = True
        for table_name in tables_to_verify:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.scalar()
            status = "✓ 已清空" if count == 0 else f"✗ 剩余 {count} 条"
            print(f"{table_name}: {status}")
            if count > 0:
                all_clean = False
        print("-" * 40)
        return all_clean


def main():
    """
    主函数
    """
    print("\n" + "=" * 60)
    print("警告: 此操作将清除以下表的所有数据:")
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
