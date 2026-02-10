import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import Base
from app.models.periodic_inspection import PeriodicInspection
from app.models.temporary_repair import TemporaryRepair
from app.models.spot_work import SpotWork
from app.models.project_info import ProjectInfo
from app.models.maintenance_plan import MaintenancePlan
from app.models.personnel import Personnel
from app.models.inspection_item import InspectionItem
from app.models.spare_parts_stock import SparePartsStock
from app.models.spare_parts_inbound import SparePartsInbound

print("=" * 100)
print("手动创建数据库表")
print("=" * 100)

try:
    print("\n正在创建所有表...")
    Base.metadata.create_all(bind=engine, checkfirst=False)
    print("✅ 数据库表创建成功！")
    
    print("\n已创建的表:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")
    
except Exception as e:
    print(f"\n❌ 创建数据库表失败: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 100)
print("检查完成")
print("=" * 100)
