-- 迁移脚本：更新 work_order_operation_log 表结构
-- 将 operation_type 字段拆分为 operation_type_code 和 operation_type_name

-- 添加新字段
ALTER TABLE work_order_operation_log ADD COLUMN IF NOT EXISTS operation_type_code VARCHAR(50);
ALTER TABLE work_order_operation_log ADD COLUMN IF NOT EXISTS operation_type_name VARCHAR(50);

-- 迁移旧数据
UPDATE work_order_operation_log 
SET operation_type_code = operation_type, 
    operation_type_name = operation_type 
WHERE operation_type_code IS NULL;

-- 设置新字段为非空
ALTER TABLE work_order_operation_log ALTER COLUMN operation_type_code SET NOT NULL;
ALTER TABLE work_order_operation_log ALTER COLUMN operation_type_name SET NOT NULL;

-- 删除旧字段
ALTER TABLE work_order_operation_log DROP COLUMN IF EXISTS operation_type;
