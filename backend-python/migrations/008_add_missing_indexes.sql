-- 迁移脚本：添加缺失索引
-- 提升查询性能

-- 1. project_info 表 - project_manager 字段
-- 用于查询运维人员关联的项目
CREATE INDEX IF NOT EXISTS idx_project_info_project_manager ON project_info(project_manager);

-- 2. spot_work_worker 表 - id_card_number 字段
-- 用于身份证号查询
CREATE INDEX IF NOT EXISTS idx_spot_work_worker_id_card ON spot_work_worker(id_card_number);

-- 3. spot_work_worker 表 - name 字段
-- 用于姓名查询
CREATE INDEX IF NOT EXISTS idx_spot_work_worker_name ON spot_work_worker(name);

-- 4. weekly_report 表 - is_deleted 字段
-- 用于软删除查询
CREATE INDEX IF NOT EXISTS idx_weekly_report_is_deleted ON weekly_report(is_deleted);

-- 5. maintenance_log 表 - is_deleted 字段
-- 用于软删除查询
CREATE INDEX IF NOT EXISTS idx_maintenance_log_is_deleted ON maintenance_log(is_deleted);

-- 添加日志记录
INSERT INTO system_log (log_type, log_content, created_at)
SELECT 'MIGRATION', '添加缺失索引完成', NOW()
WHERE NOT EXISTS (SELECT 1 FROM system_log WHERE log_content LIKE '%添加缺失索引完成%');
