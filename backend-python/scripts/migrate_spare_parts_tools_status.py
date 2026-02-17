"""
数据库迁移脚本：为备品备件和维修工具添加状态字段
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine
from sqlalchemy import text


def migrate():
    """执行数据库迁移"""
    with engine.connect() as conn:
        print("开始迁移备品备件和维修工具状态字段...")
        
        # 1. 为 spare_parts_stock 表添加 status 字段
        try:
            conn.execute(text("""
                ALTER TABLE spare_parts_stock 
                ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT '在库'
            """))
            print("✓ spare_parts_stock 表添加 status 字段成功")
        except Exception as e:
            print(f"✗ spare_parts_stock 表添加 status 字段失败: {e}")
        
        # 2. 为 spare_parts_stock 表创建状态索引
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_spare_parts_status ON spare_parts_stock(status)
            """))
            print("✓ spare_parts_stock 表创建 status 索引成功")
        except Exception as e:
            print(f"✗ spare_parts_stock 表创建 status 索引失败: {e}")
        
        # 3. 为 spare_parts_usage 表添加 stock_id 字段
        try:
            conn.execute(text("""
                ALTER TABLE spare_parts_usage 
                ADD COLUMN IF NOT EXISTS stock_id BIGINT
            """))
            print("✓ spare_parts_usage 表添加 stock_id 字段成功")
        except Exception as e:
            print(f"✗ spare_parts_usage 表添加 stock_id 字段失败: {e}")
        
        # 4. 为 spare_parts_usage 表添加 status 字段
        try:
            conn.execute(text("""
                ALTER TABLE spare_parts_usage 
                ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT '已使用'
            """))
            print("✓ spare_parts_usage 表添加 status 字段成功")
        except Exception as e:
            print(f"✗ spare_parts_usage 表添加 status 字段失败: {e}")
        
        # 5. 为 spare_parts_usage 表创建状态索引
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_usage_status ON spare_parts_usage(status)
            """))
            print("✓ spare_parts_usage 表创建 status 索引成功")
        except Exception as e:
            print(f"✗ spare_parts_usage 表创建 status 索引失败: {e}")
        
        # 6. 为 repair_tools_stock 表添加 status 字段
        try:
            conn.execute(text("""
                ALTER TABLE repair_tools_stock 
                ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT '已归还'
            """))
            print("✓ repair_tools_stock 表添加 status 字段成功")
        except Exception as e:
            print(f"✗ repair_tools_stock 表添加 status 字段失败: {e}")
        
        # 7. 为 repair_tools_stock 表创建状态索引
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_repair_tool_status ON repair_tools_stock(status)
            """))
            print("✓ repair_tools_stock 表创建 status 索引成功")
        except Exception as e:
            print(f"✗ repair_tools_stock 表创建 status 索引失败: {e}")
        
        # 8. 更新现有数据的状态
        # 更新 spare_parts_stock：库存为0的设为缺货
        try:
            conn.execute(text("""
                UPDATE spare_parts_stock SET status = '缺货' WHERE quantity = 0
            """))
            print("✓ 更新 spare_parts_stock 缺货状态成功")
        except Exception as e:
            print(f"✗ 更新 spare_parts_stock 缺货状态失败: {e}")
        
        # 提交事务
        conn.commit()
        
        print("\n迁移完成！")
        print("\n状态说明：")
        print("备品备件库存(spare_parts_stock)：在库、已使用、缺货")
        print("备品备件领用(spare_parts_usage)：已使用")
        print("维修工具库存(repair_tools_stock)：已归还、已领用、已损坏")
        print("维修工具领用(repair_tools_issue)：已领用、已归还、已损坏")


if __name__ == "__main__":
    migrate()
