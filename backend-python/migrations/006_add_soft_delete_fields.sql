-- 添加软删除字段到工单表
-- 执行日期: 2026-02-26
-- 说明: 为定期巡检单、临时维修单、零星用工单添加软删除字段

-- 1. 为定期巡检单表添加软删除字段
ALTER TABLE periodic_inspection 
ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;

ALTER TABLE periodic_inspection 
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;

ALTER TABLE periodic_inspection 
ADD COLUMN IF NOT EXISTS deleted_by BIGINT;

COMMENT ON COLUMN periodic_inspection.is_deleted IS '是否已删除';
COMMENT ON COLUMN periodic_inspection.deleted_at IS '删除时间';
COMMENT ON COLUMN periodic_inspection.deleted_by IS '删除人ID';

-- 添加索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_periodic_is_deleted ON periodic_inspection(is_deleted);

-- 2. 为临时维修单表添加软删除字段
ALTER TABLE temporary_repair 
ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;

ALTER TABLE temporary_repair 
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;

ALTER TABLE temporary_repair 
ADD COLUMN IF NOT EXISTS deleted_by BIGINT;

COMMENT ON COLUMN temporary_repair.is_deleted IS '是否已删除';
COMMENT ON COLUMN temporary_repair.deleted_at IS '删除时间';
COMMENT ON COLUMN temporary_repair.deleted_by IS '删除人ID';

-- 添加索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_temp_repair_is_deleted ON temporary_repair(is_deleted);

-- 3. 为零星用工单表添加软删除字段
ALTER TABLE spot_work 
ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;

ALTER TABLE spot_work 
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;

ALTER TABLE spot_work 
ADD COLUMN IF NOT EXISTS deleted_by BIGINT;

COMMENT ON COLUMN spot_work.is_deleted IS '是否已删除';
COMMENT ON COLUMN spot_work.deleted_at IS '删除时间';
COMMENT ON COLUMN spot_work.deleted_by IS '删除人ID';

-- 添加索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_spot_work_is_deleted ON spot_work(is_deleted);

-- 4. 更新现有数据，确保所有记录的is_deleted字段都有值
UPDATE periodic_inspection SET is_deleted = FALSE WHERE is_deleted IS NULL;
UPDATE temporary_repair SET is_deleted = FALSE WHERE is_deleted IS NULL;
UPDATE spot_work SET is_deleted = FALSE WHERE is_deleted IS NULL;
