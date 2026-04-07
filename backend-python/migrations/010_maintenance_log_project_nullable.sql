-- 修改 maintenance_log 表的 project_id 和 project_name 字段为可空
-- 允许维保日志不关联项目

ALTER TABLE maintenance_log 
ALTER COLUMN project_id DROP NOT NULL;

ALTER TABLE maintenance_log 
ALTER COLUMN project_name DROP NOT NULL;
