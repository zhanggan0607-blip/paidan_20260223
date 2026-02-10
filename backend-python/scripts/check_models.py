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
print("数据库模型字段检查报告")
print("=" * 100)

models = {
    'personnel': Personnel,
    'maintenance_plan': MaintenancePlan,
    'project_info': ProjectInfo,
    'periodic_inspection': PeriodicInspection,
    'temporary_repair': TemporaryRepair,
    'spot_work': SpotWork,
    'inspection_item': InspectionItem,
    'spare_parts_stock': SparePartsStock,
    'spare_parts_inbound': SparePartsInbound,
}

for model_name, model_class in models.items():
    print(f"\n{'=' * 100}")
    print(f"表名: {model_name}")
    print(f"{'=' * 100}")
    
    columns = model_class.__table__.columns
    print(f"\n字段数量: {len(columns)}")
    print("\n字段列表:")
    
    for col in columns:
        nullable_str = "NULL" if col.nullable else "NOT NULL"
        default_str = f" DEFAULT {col.default}" if col.default is not None else ""
        unique_str = " UNIQUE" if col.unique else ""
        type_str = str(col.type)
        
        print(f"  - {col.name:30} {type_str:30} {nullable_str}{default_str}{unique_str}")
        if col.comment:
            print(f"    注释: {col.comment}")

print(f"\n{'=' * 100}")
print("检查完成")
print(f"{'=' * 100}")
