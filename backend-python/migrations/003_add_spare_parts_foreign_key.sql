-- 为备品备件领用表添加外键约束
-- 关联 spare_parts_usage.stock_id -> spare_parts_stock.id

-- 1. 首先为 stock_id 列创建索引（如果不存在）
CREATE INDEX IF NOT EXISTS idx_usage_stock_id ON spare_parts_usage(stock_id);

-- 2. 更新现有的领用记录，根据产品名称、品牌、型号匹配库存记录ID
UPDATE spare_parts_usage spu
SET stock_id = (
    SELECT s.id 
    FROM spare_parts_stock s 
    WHERE s.product_name = spu.product_name 
    AND COALESCE(s.brand, '') = COALESCE(spu.brand, '')
    AND COALESCE(s.model, '') = COALESCE(spu.model, '')
    LIMIT 1
)
WHERE stock_id IS NULL;

-- 3. 添加外键约束
-- 注意：如果存在不匹配的记录，需要先处理这些记录
ALTER TABLE spare_parts_usage 
DROP CONSTRAINT IF EXISTS fk_spare_parts_usage_stock_id;

ALTER TABLE spare_parts_usage 
ADD CONSTRAINT fk_spare_parts_usage_stock_id 
FOREIGN KEY (stock_id) REFERENCES spare_parts_stock(id) 
ON DELETE SET NULL;

-- 迁移完成提示
-- 执行此脚本后，spare_parts_usage 表的 stock_id 字段将与 spare_parts_stock 表建立外键关联
