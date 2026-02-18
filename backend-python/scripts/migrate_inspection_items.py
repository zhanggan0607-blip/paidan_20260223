"""
数据迁移脚本：修复 maintenance_plan 表中 inspection_items 字段的层级映射问题

问题描述：
- inspection_item 字段错误地存储了第1级的名称（应该存储第2级）
- inspection_content 字段错误地存储了第2级的名称（应该存储第3级）

修复方案：
- inspection_item 应该从第2级（level=2）获取 item_name
- inspection_content 应该从第3级（level=3）获取 item_name

运行方式：
cd D:\共享文件\SSTCP-paidan260120\backend-python
python scripts/migrate_inspection_items.py
"""

import sys
import os
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.maintenance_plan import MaintenancePlan
from app.models.inspection_item import InspectionItem


def get_item_name_by_id(db: Session, item_id: int) -> str:
    """
    根据ID获取巡查项名称
    
    Args:
        db: 数据库会话
        item_id: 巡查项ID
        
    Returns:
        巡查项名称，如果不存在返回空字符串
    """
    if not item_id:
        return ''
    
    item = db.query(InspectionItem).filter(InspectionItem.id == item_id).first()
    if item:
        return item.item_name
    return ''


def fix_inspection_items(db: Session) -> dict:
    """
    修复所有维保计划的 inspection_items 字段
    
    Args:
        db: 数据库会话
        
    Returns:
        修复结果统计
    """
    stats = {
        'total': 0,
        'fixed': 0,
        'skipped': 0,
        'errors': 0,
        'details': []
    }
    
    plans = db.query(MaintenancePlan).all()
    stats['total'] = len(plans)
    
    for plan in plans:
        try:
            if not plan.inspection_items:
                stats['skipped'] += 1
                continue
            
            items_data = json.loads(plan.inspection_items)
            
            if not isinstance(items_data, list) or len(items_data) == 0:
                stats['skipped'] += 1
                continue
            
            needs_update = False
            
            for item in items_data:
                level1_id = item.get('level1_id')
                level2_id = item.get('level2_id')
                level3_id = item.get('level3_id')
                
                old_inspection_item = item.get('inspection_item', '')
                old_inspection_content = item.get('inspection_content', '')
                
                new_inspection_item = get_item_name_by_id(db, level2_id)
                new_inspection_content = get_item_name_by_id(db, level3_id)
                
                if old_inspection_item != new_inspection_item or old_inspection_content != new_inspection_content:
                    item['inspection_item'] = new_inspection_item
                    item['inspection_content'] = new_inspection_content
                    needs_update = True
                    
                    stats['details'].append({
                        'plan_id': plan.plan_id,
                        'plan_name': plan.plan_name,
                        'old_item': old_inspection_item,
                        'new_item': new_inspection_item,
                        'old_content': old_inspection_content,
                        'new_content': new_inspection_content
                    })
            
            if needs_update:
                plan.inspection_items = json.dumps(items_data, ensure_ascii=False)
                db.commit()
                stats['fixed'] += 1
                print(f"已修复: {plan.plan_id} - {plan.plan_name}")
            else:
                stats['skipped'] += 1
                
        except Exception as e:
            stats['errors'] += 1
            print(f"处理失败: {plan.plan_id} - {str(e)}")
            db.rollback()
    
    return stats


def main():
    """
    主函数
    """
    print("=" * 60)
    print("开始执行数据迁移：修复 inspection_items 字段层级映射")
    print("=" * 60)
    
    db: Session = SessionLocal()
    
    try:
        stats = fix_inspection_items(db)
        
        print("\n" + "=" * 60)
        print("迁移完成！统计结果：")
        print(f"  总记录数: {stats['total']}")
        print(f"  已修复: {stats['fixed']}")
        print(f"  已跳过: {stats['skipped']}")
        print(f"  错误数: {stats['errors']}")
        
        if stats['details']:
            print("\n修复详情：")
            for detail in stats['details']:
                print(f"  计划: {detail['plan_id']} - {detail['plan_name']}")
                print(f"    巡查项: '{detail['old_item']}' -> '{detail['new_item']}'")
                print(f"    巡查内容: '{detail['old_content']}' -> '{detail['new_content']}'")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"迁移失败: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
