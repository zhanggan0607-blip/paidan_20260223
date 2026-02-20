-- 数据库迁移脚本：统一 maintenance_plan 和 work_plan 表结构
-- 执行日期：2025-02-19
-- 说明：将两个表的字段命名统一，并添加同步所需字段

-- ============================================
-- 1. 修改 maintenance_plan 表
-- ============================================

-- 1.1 将 responsible_person 改名为 maintenance_personnel
ALTER TABLE maintenance_plan RENAME COLUMN responsible_person TO maintenance_personnel;

-- 1.2 将 execution_status 改名为 status
ALTER TABLE maintenance_plan RENAME COLUMN execution_status TO status;

-- 1.3 添加 filled_count 字段（如果不存在）
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'maintenance_plan' AND column_name = 'filled_count') THEN
        ALTER TABLE maintenance_plan ADD COLUMN filled_count INTEGER DEFAULT 0;
        COMMENT ON COLUMN maintenance_plan.filled_count IS '已填写检查项数量';
    END IF;
END $$;

-- 1.4 添加 total_count 字段（如果不存在）
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'maintenance_plan' AND column_name = 'total_count') THEN
        ALTER TABLE maintenance_plan ADD COLUMN total_count INTEGER DEFAULT 5;
        COMMENT ON COLUMN maintenance_plan.total_count IS '检查项总数量';
    END IF;
END $$;

-- 1.5 修改 maintenance_personnel 字段长度（如果需要）
ALTER TABLE maintenance_plan ALTER COLUMN maintenance_personnel TYPE VARCHAR(100);

-- 1.6 修改 maintenance_personnel 允许为空
ALTER TABLE maintenance_plan ALTER COLUMN maintenance_personnel DROP NOT NULL;

-- 1.7 删除旧索引（如果存在）
DROP INDEX IF EXISTS idx_maintenance_execution_status;

-- 1.8 创建新索引
CREATE INDEX IF NOT EXISTS idx_maintenance_status ON maintenance_plan(status);
CREATE INDEX IF NOT EXISTS idx_maintenance_personnel ON maintenance_plan(maintenance_personnel);

-- ============================================
-- 2. 修改 work_plan 表
-- ============================================

-- 2.1 添加 plan_name 字段（如果不存在）
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'work_plan' AND column_name = 'plan_name') THEN
        ALTER TABLE work_plan ADD COLUMN plan_name VARCHAR(200);
        COMMENT ON COLUMN work_plan.plan_name IS '计划名称';
    END IF;
END $$;

-- ============================================
-- 3. 更新表注释
-- ============================================

COMMENT ON COLUMN maintenance_plan.maintenance_personnel IS '运维人员';
COMMENT ON COLUMN maintenance_plan.status IS '执行状态';
COMMENT ON COLUMN work_plan.plan_name IS '计划名称';

-- ============================================
-- 4. 数据迁移（可选）
-- ============================================

-- 4.1 如果 work_plan 中有数据，同步到 maintenance_plan
-- 注意：这个操作需要根据实际业务需求决定是否执行
-- INSERT INTO maintenance_plan (plan_id, plan_name, project_id, project_name, plan_type, ...)
-- SELECT plan_id, plan_name, project_id, project_name, plan_type, ... FROM work_plan
-- WHERE NOT EXISTS (SELECT 1 FROM maintenance_plan mp WHERE mp.plan_id = work_plan.plan_id);

-- ============================================
-- 完成
-- ============================================
-- 迁移完成，请验证数据一致性
