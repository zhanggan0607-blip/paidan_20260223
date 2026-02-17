"""
数据一致性检查和修复脚本
检查WorkPlan表与三种工单表之间的数据一致性，并修复不一致的数据
"""
from datetime import datetime
from app.database import SessionLocal
from app.models.work_plan import WorkPlan
from app.models.periodic_inspection import PeriodicInspection
from app.models.temporary_repair import TemporaryRepair
from app.models.spot_work import SpotWork
from app.services.sync_service import SyncService, PLAN_TYPE_INSPECTION, PLAN_TYPE_REPAIR, PLAN_TYPE_SPOTWORK


def check_and_fix_consistency(dry_run: bool = True):
    """
    检查并修复数据一致性
    
    Args:
        dry_run: True表示只检查不修复，False表示执行修复
    """
    db = SessionLocal()
    sync_service = SyncService(db)
    
    try:
        print("=" * 80)
        print("数据一致性检查和修复脚本")
        print(f"模式: {'仅检查(不修复)' if dry_run else '检查并修复'}")
        print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        issues_found = 0
        issues_fixed = 0
        
        print("\n" + "-" * 80)
        print("1. 检查定期巡检工单与WorkPlan的一致性")
        print("-" * 80)
        
        inspections = db.query(PeriodicInspection).all()
        print(f"定期巡检工单总数: {len(inspections)}")
        
        for inspection in inspections:
            work_plan = db.query(WorkPlan).filter(WorkPlan.plan_id == inspection.inspection_id).first()
            
            if not work_plan:
                issues_found += 1
                print(f"  [缺失] WorkPlan中缺少定期巡检工单: {inspection.inspection_id}")
                if not dry_run:
                    sync_service.sync_order_to_work_plan(PLAN_TYPE_INSPECTION, inspection)
                    issues_fixed += 1
                    print(f"  [已修复] 已同步到WorkPlan: {inspection.inspection_id}")
            else:
                if _check_data_mismatch(work_plan, inspection):
                    issues_found += 1
                    print(f"  [不一致] 数据不匹配: {inspection.inspection_id}")
                    if not dry_run:
                        sync_service.sync_order_to_work_plan(PLAN_TYPE_INSPECTION, inspection)
                        issues_fixed += 1
                        print(f"  [已修复] 已更新WorkPlan: {inspection.inspection_id}")
        
        print("\n" + "-" * 80)
        print("2. 检查临时维修工单与WorkPlan的一致性")
        print("-" * 80)
        
        repairs = db.query(TemporaryRepair).all()
        print(f"临时维修工单总数: {len(repairs)}")
        
        for repair in repairs:
            work_plan = db.query(WorkPlan).filter(WorkPlan.plan_id == repair.repair_id).first()
            
            if not work_plan:
                issues_found += 1
                print(f"  [缺失] WorkPlan中缺少临时维修工单: {repair.repair_id}")
                if not dry_run:
                    sync_service.sync_order_to_work_plan(PLAN_TYPE_REPAIR, repair)
                    issues_fixed += 1
                    print(f"  [已修复] 已同步到WorkPlan: {repair.repair_id}")
            else:
                if _check_data_mismatch(work_plan, repair):
                    issues_found += 1
                    print(f"  [不一致] 数据不匹配: {repair.repair_id}")
                    if not dry_run:
                        sync_service.sync_order_to_work_plan(PLAN_TYPE_REPAIR, repair)
                        issues_fixed += 1
                        print(f"  [已修复] 已更新WorkPlan: {repair.repair_id}")
        
        print("\n" + "-" * 80)
        print("3. 检查零星用工工单与WorkPlan的一致性")
        print("-" * 80)
        
        spotworks = db.query(SpotWork).all()
        print(f"零星用工工单总数: {len(spotworks)}")
        
        for spotwork in spotworks:
            work_plan = db.query(WorkPlan).filter(WorkPlan.plan_id == spotwork.work_id).first()
            
            if not work_plan:
                issues_found += 1
                print(f"  [缺失] WorkPlan中缺少零星用工工单: {spotwork.work_id}")
                if not dry_run:
                    sync_service.sync_order_to_work_plan(PLAN_TYPE_SPOTWORK, spotwork)
                    issues_fixed += 1
                    print(f"  [已修复] 已同步到WorkPlan: {spotwork.work_id}")
            else:
                if _check_data_mismatch(work_plan, spotwork):
                    issues_found += 1
                    print(f"  [不一致] 数据不匹配: {spotwork.work_id}")
                    if not dry_run:
                        sync_service.sync_order_to_work_plan(PLAN_TYPE_SPOTWORK, spotwork)
                        issues_fixed += 1
                        print(f"  [已修复] 已更新WorkPlan: {spotwork.work_id}")
        
        print("\n" + "-" * 80)
        print("4. 检查WorkPlan中孤立记录(对应工单不存在)")
        print("-" * 80)
        
        work_plans = db.query(WorkPlan).all()
        print(f"WorkPlan总数: {len(work_plans)}")
        
        orphan_count = 0
        for wp in work_plans:
            exists = False
            if wp.plan_type == PLAN_TYPE_INSPECTION:
                exists = db.query(PeriodicInspection).filter(
                    PeriodicInspection.inspection_id == wp.plan_id
                ).first() is not None
            elif wp.plan_type == PLAN_TYPE_REPAIR:
                exists = db.query(TemporaryRepair).filter(
                    TemporaryRepair.repair_id == wp.plan_id
                ).first() is not None
            elif wp.plan_type == PLAN_TYPE_SPOTWORK:
                exists = db.query(SpotWork).filter(
                    SpotWork.work_id == wp.plan_id
                ).first() is not None
            
            if not exists:
                orphan_count += 1
                issues_found += 1
                print(f"  [孤立] WorkPlan记录无对应工单: {wp.plan_id} (类型: {wp.plan_type})")
                if not dry_run:
                    if wp.plan_type == PLAN_TYPE_INSPECTION:
                        sync_service.sync_work_plan_to_order(wp)
                    elif wp.plan_type == PLAN_TYPE_REPAIR:
                        sync_service.sync_work_plan_to_order(wp)
                    elif wp.plan_type == PLAN_TYPE_SPOTWORK:
                        sync_service.sync_work_plan_to_order(wp)
                    issues_fixed += 1
                    print(f"  [已修复] 已创建对应工单: {wp.plan_id}")
        
        print("\n" + "=" * 80)
        print("检查结果汇总")
        print("=" * 80)
        print(f"发现的问题数量: {issues_found}")
        if not dry_run:
            print(f"修复的问题数量: {issues_fixed}")
        else:
            print("提示: 使用 --fix 参数执行实际修复")
        print("=" * 80)
        
        print("\n" + "-" * 80)
        print("5. 数据统计对比")
        print("-" * 80)
        
        inspection_count = db.query(PeriodicInspection).count()
        repair_count = db.query(TemporaryRepair).count()
        spotwork_count = db.query(SpotWork).count()
        work_plan_inspection = db.query(WorkPlan).filter(WorkPlan.plan_type == PLAN_TYPE_INSPECTION).count()
        work_plan_repair = db.query(WorkPlan).filter(WorkPlan.plan_type == PLAN_TYPE_REPAIR).count()
        work_plan_spotwork = db.query(WorkPlan).filter(WorkPlan.plan_type == PLAN_TYPE_SPOTWORK).count()
        
        print(f"定期巡检工单表: {inspection_count} 条")
        print(f"WorkPlan(定期巡检): {work_plan_inspection} 条")
        print(f"差异: {inspection_count - work_plan_inspection} 条")
        print()
        print(f"临时维修工单表: {repair_count} 条")
        print(f"WorkPlan(临时维修): {work_plan_repair} 条")
        print(f"差异: {repair_count - work_plan_repair} 条")
        print()
        print(f"零星用工工单表: {spotwork_count} 条")
        print(f"WorkPlan(零星用工): {work_plan_spotwork} 条")
        print(f"差异: {spotwork_count - work_plan_spotwork} 条")
        
    except Exception as e:
        db.rollback()
        print(f"执行过程出错: {str(e)}")
        raise
    finally:
        db.close()


def _check_data_mismatch(work_plan: WorkPlan, order) -> bool:
    """检查WorkPlan与工单数据是否不一致"""
    if work_plan.project_id != order.project_id:
        return True
    if work_plan.status != order.status:
        return True
    if work_plan.maintenance_personnel != order.maintenance_personnel:
        return True
    
    wp_start = work_plan.plan_start_date
    order_start = order.plan_start_date
    if isinstance(wp_start, datetime):
        wp_start = wp_start.date()
    if isinstance(order_start, datetime):
        order_start = order_start.date()
    if wp_start != order_start:
        return True
    
    wp_end = work_plan.plan_end_date
    order_end = order.plan_end_date
    if isinstance(wp_end, datetime):
        wp_end = wp_end.date()
    if isinstance(order_end, datetime):
        order_end = order_end.date()
    if wp_end != order_end:
        return True
    
    return False


if __name__ == "__main__":
    import sys
    
    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == '--fix':
        dry_run = False
    
    check_and_fix_consistency(dry_run=dry_run)
