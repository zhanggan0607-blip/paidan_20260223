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
print("检查所有表的索引名称")
print("=" * 100)

all_indexes = []

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
    print(f"\n{model_name}:")
    table_args = model_class.__table_args__
    if isinstance(table_args, tuple) and len(table_args) > 0:
        for item in table_args[0]:
            if isinstance(item, tuple):
                idx_name = item[0]
            else:
                idx_name = str(item)
            print(f"  - {idx_name}")
            all_indexes.append(idx_name)

print(f"\n{'=' * 100}")
print(f"所有索引名称: {all_indexes}")
print(f"{'=' * 100}")

duplicates = [idx for idx in all_indexes if all_indexes.count(idx) > 1]
if duplicates:
    print(f"\n⚠️  重复的索引名称: {set(duplicates)}")
else:
    print("\n✅ 没有重复的索引名称")
