"""
将维保计划中的定期维保数据同步到定期巡检工单表
"""
from datetime import datetime
from app.database import SessionLocal
from app.models.maintenance_plan import MaintenancePlan
from app.models.periodic_inspection import PeriodicInspection
from app.models.project_info import ProjectInfo


def sync_periodic_inspection():
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("开始同步定期维保计划到定期巡检工单表")
        print("=" * 60)
        
        maintenance_plans = db.query(MaintenancePlan).filter(
            MaintenancePlan.plan_type == '定期维保'
        ).all()
        
        print(f"\n找到 {len(maintenance_plans)} 条定期维保计划")
        
        synced_count = 0
        skipped_count = 0
        error_count = 0
        
        for plan in maintenance_plans:
            existing = db.query(PeriodicInspection).filter(
                PeriodicInspection.inspection_id == plan.plan_id
            ).first()
            
            if existing:
                skipped_count += 1
                continue
            
            project = db.query(ProjectInfo).filter(
                ProjectInfo.project_id == plan.project_id
            ).first()
            
            project_name = project.project_name if project else plan.project_name or ''
            client_name = project.client_name if project else ''
            
            try:
                inspection = PeriodicInspection(
                    inspection_id=plan.plan_id,
                    project_id=plan.project_id,
                    project_name=project_name,
                    plan_start_date=plan.plan_start_date,
                    plan_end_date=plan.plan_end_date,
                    client_name=client_name,
                    maintenance_personnel=plan.responsible_person,
                    status=map_status(plan.plan_status),
                    filled_count=0,
                    total_count=5,
                    remarks=plan.remarks
                )
                
                db.add(inspection)
                synced_count += 1
                
                if synced_count % 50 == 0:
                    db.commit()
                    print(f"已同步 {synced_count} 条...")
                    
            except Exception as e:
                error_count += 1
                print(f"同步失败: plan_id={plan.plan_id}, 错误: {str(e)}")
        
        db.commit()
        
        print("\n" + "=" * 60)
        print("同步完成!")
        print(f"  - 成功同步: {synced_count} 条")
        print(f"  - 跳过已存在: {skipped_count} 条")
        print(f"  - 失败: {error_count} 条")
        print("=" * 60)
        
        final_count = db.query(PeriodicInspection).count()
        print(f"\nperiodic_inspection 表当前记录数: {final_count}")
        
    except Exception as e:
        db.rollback()
        print(f"同步过程出错: {str(e)}")
        raise
    finally:
        db.close()


def map_status(plan_status: str) -> str:
    """将维保计划状态映射到工单状态"""
    status_mapping = {
        '待执行': '待执行',
        '执行中': '执行中',
        '已完成': '已完成',
        '待审批': '待审批',
        '已退回': '已退回',
        '待确认': '待确认',
        '未进行': '未进行',
    }
    return status_mapping.get(plan_status, '未进行')


if __name__ == "__main__":
    sync_periodic_inspection()
