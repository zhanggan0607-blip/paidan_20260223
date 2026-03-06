-- 修改 is_deleted 字段类型从 integer 改为 boolean
-- 执行时间: 2026-03-05
-- 说明: 统一所有表的 is_deleted 字段为 boolean 类型

-- 1. work_plan 表
ALTER TABLE work_plan ALTER COLUMN is_deleted TYPE boolean USING (is_deleted::integer::boolean);

-- 2. maintenance_plan 表
ALTER TABLE maintenance_plan ALTER COLUMN is_deleted TYPE boolean USING (is_deleted::integer::boolean);

-- 3. periodic_inspection 表
ALTER TABLE periodic_inspection ALTER COLUMN is_deleted TYPE boolean USING (is_deleted::integer::boolean);

-- 4. temporary_repair 表
ALTER TABLE temporary_repair ALTER COLUMN is_deleted TYPE boolean USING (is_deleted::integer::boolean);

-- 5. spot_work 表
ALTER TABLE spot_work ALTER COLUMN is_deleted TYPE boolean USING (is_deleted::integer::boolean);

-- 6. weekly_report 表
ALTER TABLE weekly_report ALTER COLUMN is_deleted TYPE boolean USING (is_deleted::integer::boolean);

-- 7. maintenance_log 表
ALTER TABLE maintenance_log ALTER COLUMN is_deleted TYPE boolean USING (is_deleted::integer::boolean);

-- 8. project_info 表 (如果存在)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'project_info' AND column_name = 'is_deleted') THEN
        ALTER TABLE project_info ALTER COLUMN is_deleted TYPE boolean USING (is_deleted::integer::boolean);
    END IF;
END $$;

-- 9. personnel 表 (如果存在)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'personnel' AND column_name = 'is_deleted') THEN
        ALTER TABLE personnel ALTER COLUMN is_deleted TYPE boolean USING (is_deleted::integer::boolean);
    END IF;
END $$;

-- 10. spare_parts_stock 表 (如果存在)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'spare_parts_stock' AND column_name = 'is_deleted') THEN
        ALTER TABLE spare_parts_stock ALTER COLUMN is_deleted TYPE boolean USING (is_deleted::integer::boolean);
    END IF;
END $$;

-- 11. repair_tools_stock 表 (如果存在)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'repair_tools_stock' AND column_name = 'is_deleted') THEN
        ALTER TABLE repair_tools_stock ALTER COLUMN is_deleted TYPE boolean USING (is_deleted::integer::boolean);
    END IF;
END $$;
