-- SSTCP维保系统初始化数据脚本
-- 执行时间：部署后首次运行

-- 插入默认管理员账户
INSERT INTO personnel (name, gender, phone, department, role, address, remarks) VALUES
('管理员', '男', '13800000001', '管理部', '管理员', '公司总部', '系统默认管理员账户'),
('部门经理', '男', '13800000002', '运维部', '部门经理', '公司总部', '系统默认部门经理账户'),
('运维员1', '男', '13800000003', '运维部', '运维人员', '公司总部', '系统默认运维人员账户'),
('运维员2', '男', '13800000004', '运维部', '运维人员', '公司总部', '系统默认运维人员账户'),
('材料员', '女', '13800000005', '物资部', '材料员', '公司总部', '系统默认材料员账户');

-- 插入默认项目信息
INSERT INTO project_info (project_code, project_name, project_address, project_leader, leader_phone, start_date, status, description) VALUES
('PRJ001', '示范项目', '浙江省杭州市', '项目负责人', '13900000001', CURRENT_DATE, '进行中', '系统默认示范项目');

-- 插入默认字典数据
INSERT INTO dictionary (dict_type, dict_code, dict_label, dict_value, sort_order, status, remark) VALUES
('gender', 'male', '男', '男', 1, '启用', '性别'),
('gender', 'female', '女', '女', 2, '启用', '性别'),
('role', 'admin', '管理员', '管理员', 1, '启用', '角色'),
('role', 'manager', '部门经理', '部门经理', 2, '启用', '角色'),
('role', 'operator', '运维人员', '运维人员', 3, '启用', '角色'),
('role', 'material', '材料员', '材料员', 4, '启用', '角色'),
('work_status', 'pending', '待执行', '待执行', 1, '启用', '工单状态'),
('work_status', 'in_progress', '执行中', '执行中', 2, '启用', '工单状态'),
('work_status', 'completed', '已完成', '已完成', 3, '启用', '工单状态'),
('work_status', 'returned', '已退回', '已退回', 4, '启用', '工单状态');

-- 输出提示信息
SELECT '初始化数据完成！' as message;
SELECT '默认账户信息：' as info;
SELECT name as 用户名, phone as 手机号, role as 角色, RIGHT(phone, 6) as 默认密码 FROM personnel;
