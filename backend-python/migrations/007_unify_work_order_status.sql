-- 迁移脚本：统一工单状态为4种
-- 执行中、待确认、已完成、已退回
-- 将未下发、待执行、未进行合并为执行中

-- 更新定期巡检单状态
UPDATE periodic_inspection 
SET status = '执行中' 
WHERE status IN ('未下发', '待执行', '未进行');

-- 更新临时维修单状态
UPDATE temporary_repair 
SET status = '执行中' 
WHERE status IN ('未下发', '待执行', '未进行');

-- 更新零星用工单状态
UPDATE spot_work 
SET status = '执行中' 
WHERE status IN ('未下发', '待执行', '未进行');

-- 更新维保计划状态
UPDATE maintenance_plan 
SET status = '执行中' 
WHERE status IN ('未下发', '待执行', '未进行');

-- 更新工单计划状态
UPDATE work_plan 
SET status = '执行中' 
WHERE status IN ('未下发', '待执行', '未进行');

-- 更新字典表中的状态值
UPDATE dictionary 
SET dict_value = '执行中' 
WHERE dict_value IN ('未下发', '待执行', '未进行') 
AND dict_type LIKE '%status%';

-- 添加日志记录
INSERT INTO system_log (log_type, log_content, created_at)
SELECT 'MIGRATION', '统一工单状态迁移完成：将未下发、待执行、未进行合并为执行中', NOW()
WHERE NOT EXISTS (SELECT 1 FROM system_log WHERE log_content LIKE '%统一工单状态迁移完成%');
