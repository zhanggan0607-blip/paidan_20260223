"""
数据库迁移脚本：将三个工单表合并为统一的工作计划表

此脚本将：
1. 创建新的 work_plan 表
2. 将 spot_work、periodic_inspection、temporary_repair 表的数据迁移到 work_plan 表
3. 将原来的编号字段统一改为 plan_id（计划编号）

使用方法：
    python scripts/migrate_to_work_plan.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine, SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_work_plan_table():
    """创建 work_plan 表"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS work_plan (
        id BIGSERIAL PRIMARY KEY,
        plan_id VARCHAR(50) NOT NULL UNIQUE,
        plan_type VARCHAR(20) NOT NULL,
        project_id VARCHAR(50) NOT NULL,
        project_name VARCHAR(200) NOT NULL,
        plan_start_date TIMESTAMP NOT NULL,
        plan_end_date TIMESTAMP NOT NULL,
        client_name VARCHAR(100),
        maintenance_personnel VARCHAR(100),
        status VARCHAR(20) NOT NULL DEFAULT '未进行',
        remarks TEXT,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_work_plan_project FOREIGN KEY (project_id) REFERENCES project_info(project_id)
    );
    
    -- 创建索引
    CREATE INDEX IF NOT EXISTS idx_work_plan_id ON work_plan(plan_id);
    CREATE INDEX IF NOT EXISTS idx_work_plan_type ON work_plan(plan_type);
    CREATE INDEX IF NOT EXISTS idx_work_plan_project_id ON work_plan(project_id);
    CREATE INDEX IF NOT EXISTS idx_work_plan_project_name ON work_plan(project_name);
    CREATE INDEX IF NOT EXISTS idx_work_plan_client_name ON work_plan(client_name);
    CREATE INDEX IF NOT EXISTS idx_work_plan_status ON work_plan(status);
    CREATE INDEX IF NOT EXISTS idx_work_plan_start_date ON work_plan(plan_start_date);
    
    -- 添加表注释
    COMMENT ON TABLE work_plan IS '工作计划表（统一管理定期巡检、临时维修、零星用工）';
    COMMENT ON COLUMN work_plan.id IS '主键ID';
    COMMENT ON COLUMN work_plan.plan_id IS '计划编号';
    COMMENT ON COLUMN work_plan.plan_type IS '工单类型：定期巡检/临时维修/零星用工';
    COMMENT ON COLUMN work_plan.project_id IS '项目编号';
    COMMENT ON COLUMN work_plan.project_name IS '项目名称';
    COMMENT ON COLUMN work_plan.plan_start_date IS '计划开始日期';
    COMMENT ON COLUMN work_plan.plan_end_date IS '计划结束日期';
    COMMENT ON COLUMN work_plan.client_name IS '客户单位';
    COMMENT ON COLUMN work_plan.maintenance_personnel IS '运维人员';
    COMMENT ON COLUMN work_plan.status IS '状态';
    COMMENT ON COLUMN work_plan.remarks IS '备注';
    COMMENT ON COLUMN work_plan.created_at IS '创建时间';
    COMMENT ON COLUMN work_plan.updated_at IS '更新时间';
    """
    
    with engine.connect() as conn:
        conn.execute(text(create_table_sql))
        conn.commit()
        logger.info("work_plan 表创建成功")


def migrate_data():
    """迁移数据到 work_plan 表"""
    db = SessionLocal()
    
    try:
        # 迁移零星用工单数据 - 只迁移project_id存在于project_info表中的记录
        migrate_spot_work_sql = """
        INSERT INTO work_plan (plan_id, plan_type, project_id, project_name, plan_start_date, plan_end_date, 
                               client_name, maintenance_personnel, status, remarks, created_at, updated_at)
        SELECT sw.work_id, '零星用工', sw.project_id, sw.project_name, sw.plan_start_date, sw.plan_end_date,
               sw.client_name, sw.maintenance_personnel, sw.status, sw.remarks, sw.created_at, sw.updated_at
        FROM spot_work sw
        INNER JOIN project_info pi ON sw.project_id = pi.project_id
        ON CONFLICT (plan_id) DO NOTHING;
        """
        
        # 迁移定期巡检单数据
        migrate_periodic_inspection_sql = """
        INSERT INTO work_plan (plan_id, plan_type, project_id, project_name, plan_start_date, plan_end_date, 
                               client_name, maintenance_personnel, status, remarks, created_at, updated_at)
        SELECT pi.inspection_id, '定期巡检', pi.project_id, pi.project_name, pi.plan_start_date, pi.plan_end_date,
               pi.client_name, pi.maintenance_personnel, pi.status, pi.remarks, pi.created_at, pi.updated_at
        FROM periodic_inspection pi
        INNER JOIN project_info p ON pi.project_id = p.project_id
        ON CONFLICT (plan_id) DO NOTHING;
        """
        
        # 迁移临时维修单数据
        migrate_temporary_repair_sql = """
        INSERT INTO work_plan (plan_id, plan_type, project_id, project_name, plan_start_date, plan_end_date, 
                               client_name, maintenance_personnel, status, remarks, created_at, updated_at)
        SELECT tr.repair_id, '临时维修', tr.project_id, tr.project_name, tr.plan_start_date, tr.plan_end_date,
               tr.client_name, tr.maintenance_personnel, tr.status, tr.remarks, tr.created_at, tr.updated_at
        FROM temporary_repair tr
        INNER JOIN project_info p ON tr.project_id = p.project_id
        ON CONFLICT (plan_id) DO NOTHING;
        """
        
        with engine.connect() as conn:
            # 执行迁移
            result1 = conn.execute(text(migrate_spot_work_sql))
            logger.info(f"迁移零星用工单数据: {result1.rowcount} 条")
            
            result2 = conn.execute(text(migrate_periodic_inspection_sql))
            logger.info(f"迁移定期巡检单数据: {result2.rowcount} 条")
            
            result3 = conn.execute(text(migrate_temporary_repair_sql))
            logger.info(f"迁移临时维修单数据: {result3.rowcount} 条")
            
            conn.commit()
            logger.info("数据迁移完成")
            
    except Exception as e:
        logger.error(f"数据迁移失败: {str(e)}")
        raise
    finally:
        db.close()


def verify_migration():
    """验证迁移结果"""
    verify_sql = """
    SELECT 
        (SELECT COUNT(*) FROM spot_work) as spot_work_count,
        (SELECT COUNT(*) FROM periodic_inspection) as periodic_inspection_count,
        (SELECT COUNT(*) FROM temporary_repair) as temporary_repair_count,
        (SELECT COUNT(*) FROM work_plan) as work_plan_count,
        (SELECT COUNT(*) FROM work_plan WHERE plan_type = '零星用工') as spot_work_migrated,
        (SELECT COUNT(*) FROM work_plan WHERE plan_type = '定期巡检') as periodic_inspection_migrated,
        (SELECT COUNT(*) FROM work_plan WHERE plan_type = '临时维修') as temporary_repair_migrated;
    """
    
    with engine.connect() as conn:
        result = conn.execute(text(verify_sql))
        row = result.fetchone()
        
        logger.info("=" * 50)
        logger.info("迁移验证结果:")
        logger.info(f"  原始零星用工单数量: {row[0]}")
        logger.info(f"  原始定期巡检单数量: {row[1]}")
        logger.info(f"  原始临时维修单数量: {row[2]}")
        logger.info(f"  新表总记录数: {row[3]}")
        logger.info(f"  迁移的零星用工: {row[4]}")
        logger.info(f"  迁移的定期巡检: {row[5]}")
        logger.info(f"  迁移的临时维修: {row[6]}")
        logger.info("=" * 50)
        
        expected_total = row[0] + row[1] + row[2]
        if row[3] >= expected_total:
            logger.info("✓ 数据迁移验证通过")
        else:
            logger.warning(f"⚠ 数据迁移可能不完整，预期 {expected_total} 条，实际 {row[3]} 条")


def main():
    logger.info("开始数据库迁移...")
    
    try:
        # 1. 创建新表
        logger.info("步骤1: 创建 work_plan 表")
        create_work_plan_table()
        
        # 2. 迁移数据
        logger.info("步骤2: 迁移数据")
        migrate_data()
        
        # 3. 验证迁移
        logger.info("步骤3: 验证迁移结果")
        verify_migration()
        
        logger.info("数据库迁移完成！")
        logger.info("")
        logger.info("注意：原表（spot_work、periodic_inspection、temporary_repair）仍保留，")
        logger.info("      请确认新表数据正确后再手动删除原表。")
        
    except Exception as e:
        logger.error(f"迁移失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
