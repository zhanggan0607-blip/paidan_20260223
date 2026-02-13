from app.database import Base, engine
from app.models import (
    project_info,
    maintenance_plan,
    personnel,
    periodic_inspection,
    inspection_item,
    temporary_repair,
    spot_work,
    spare_parts_inbound,
    spare_parts_stock,
    customer
)
import logging

logger = logging.getLogger(__name__)

def init_database():
    """初始化数据库表"""
    print("=" * 80)
    print("初始化数据库表")
    print("=" * 80)
    
    try:
        print("\n开始创建数据库表...")
        
        Base.metadata.create_all(bind=engine, checkfirst=True)
        
        print("\n✅ 所有数据库表创建成功！\n")
        
        print("=" * 80)
        print("✅ 数据库初始化完成！")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    init_database()
