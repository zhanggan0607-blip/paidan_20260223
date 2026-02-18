"""
数据迁移脚本：修复 maintenance_plan 表中 inspection_items 字段的层级映射问题

问题描述：
- inspection_item 字段错误地存储了第1级的名称（应该存储第2级）
- inspection_content 字段错误地存储了第2级的名称（应该存储第3级）
- 旧数据没有保存 level1_id, level2_id, level3_id

修复方案：
- 根据 check_requirements 内容匹配正确的层级信息
- inspection_item 应该从第2级（level=2）获取 item_name
- inspection_content 应该从第3级（level=3）获取 item_name

运行方式：
cd D:\共享文件\SSTCP-paidan260120\backend-python
python scripts/migrate_inspection_items_v2.py
"""

import sys
import os
import json
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.maintenance_plan import MaintenancePlan
from app.models.inspection_item import InspectionItem


def build_inspection_tree(db: Session) -> dict:
    """
    构建巡查项树形结构
    
    Args:
        db: 数据库会话
        
    Returns:
        包含所有层级信息的字典
    """
    items = db.query(InspectionItem).all()
    
    tree = {
        'level1': {},
        'level2': {},
        'level3': {},
        'level3_by_parent': {}
    }
    
    for item in items:
        item_info = {
            'id': item.id,
            'name': item.item_name,
            'level': item.level,
            'parent_id': item.parent_id,
            'check_content': item.check_content or '',
            'check_standard': item.check_standard or ''
        }
        
        if item.level == 1:
            tree['level1'][item.id] = item_info
        elif item.level == 2:
            tree['level2'][item.id] = item_info
        elif item.level == 3:
            tree['level3'][item.id] = item_info
            if item.parent_id not in tree['level3_by_parent']:
                tree['level3_by_parent'][item.parent_id] = []
            tree['level3_by_parent'][item.parent_id].append(item_info)
    
    return tree


def find_matching_level3(tree: dict, check_requirements: str) -> dict:
    """
    根据 check_requirements 内容匹配第3级巡查项
    
    Args:
        tree: 巡查项树
        check_requirements: 检查要求内容
        
    Returns:
        匹配的第3级信息，包含 id, name, parent_id
    """
    if not check_requirements:
        return None
    
    check_requirements_lower = check_requirements.lower()
    
    best_match = None
    best_score = 0
    
    for level3_id, level3_info in tree['level3'].items():
        name = level3_info['name'].lower()
        check_content = level3_info['check_content'].lower()
        check_standard = level3_info['check_standard'].lower()
        
        score = 0
        if name and name in check_requirements_lower:
            score += 10
        if check_content and check_content in check_requirements_lower:
            score += 5
        if check_standard and check_standard in check_requirements_lower:
            score += 3
        
        if score > best_score:
            best_score = score
            best_match = level3_info
    
    if best_score >= 5:
        return best_match
    return None


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
    
    tree = build_inspection_tree(db)
    
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
                old_inspection_item = item.get('inspection_item', '')
                old_inspection_content = item.get('inspection_content', '')
                check_requirements = item.get('check_requirements', '')
                
                level1_id = item.get('level1_id', '')
                level2_id = item.get('level2_id', '')
                level3_id = item.get('level3_id', '')
                
                if level2_id and level3_id:
                    level2_info = tree['level2'].get(int(level2_id))
                    level3_info = tree['level3'].get(int(level3_id))
                    
                    if level2_info and level3_info:
                        new_inspection_item = level2_info['name']
                        new_inspection_content = level3_info['name']
                        
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
                else:
                    level3_match = find_matching_level3(tree, check_requirements)
                    
                    if level3_match:
                        new_level3_id = str(level3_match['id'])
                        new_level2_id = str(level3_match['parent_id'])
                        level2_info = tree['level2'].get(level3_match['parent_id'])
                        
                        if level2_info:
                            new_level1_id = str(level2_info['parent_id'])
                            new_inspection_item = level2_info['name']
                            new_inspection_content = level3_match['name']
                            
                            item['level1_id'] = new_level1_id
                            item['level2_id'] = new_level2_id
                            item['level3_id'] = new_level3_id
                            item['inspection_item'] = new_inspection_item
                            item['inspection_content'] = new_inspection_content
                            needs_update = True
                            
                            stats['details'].append({
                                'plan_id': plan.plan_id,
                                'plan_name': plan.plan_name,
                                'old_item': old_inspection_item,
                                'new_item': new_inspection_item,
                                'old_content': old_inspection_content,
                                'new_content': new_inspection_content,
                                'matched_by': 'check_requirements'
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
            for detail in stats['details'][:10]:
                print(f"  计划: {detail['plan_id']} - {detail['plan_name']}")
                print(f"    巡查项: '{detail['old_item']}' -> '{detail['new_item']}'")
                print(f"    巡查内容: '{detail['old_content']}' -> '{detail['new_content']}'")
                if detail.get('matched_by'):
                    print(f"    匹配方式: {detail['matched_by']}")
            
            if len(stats['details']) > 10:
                print(f"  ... 还有 {len(stats['details']) - 10} 条记录")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"迁移失败: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
