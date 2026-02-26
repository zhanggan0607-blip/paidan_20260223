-- 添加备品备件归还相关字段
-- 执行时间: 2026-02-26

-- 添加归还数量字段
ALTER TABLE spare_parts_usage 
ADD COLUMN IF NOT EXISTS return_quantity INTEGER DEFAULT 0;

-- 添加归还时间字段
ALTER TABLE spare_parts_usage 
ADD COLUMN IF NOT EXISTS return_time TIMESTAMP;

-- 添加备注字段
ALTER TABLE spare_parts_usage 
ADD COLUMN IF NOT EXISTS remark VARCHAR(500);

-- 修改状态字段默认值
ALTER TABLE spare_parts_usage 
ALTER COLUMN status SET DEFAULT '待归还';

-- 更新现有数据的状态
UPDATE spare_parts_usage 
SET status = '待归还' 
WHERE status = '已使用' OR status IS NULL;

-- 添加索引
CREATE INDEX IF NOT EXISTS idx_usage_return_time ON spare_parts_usage(return_time);

-- 添加字段注释
COMMENT ON COLUMN spare_parts_usage.return_quantity IS '归还数量';
COMMENT ON COLUMN spare_parts_usage.return_time IS '归还时间';
COMMENT ON COLUMN spare_parts_usage.remark IS '备注';
