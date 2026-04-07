-- 创建维保周报表
-- 执行时间: 2025-02-19
-- 说明: 将维保周报从maintenance_log表中独立出来，创建专用的weekly_report表

-- 检查表是否已存在
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'weekly_report') THEN
        -- 创建weekly_report表
        CREATE TABLE weekly_report (
            id BIGSERIAL PRIMARY KEY,
            report_id VARCHAR(50) UNIQUE NOT NULL,
            project_id VARCHAR(50) NOT NULL,
            project_name VARCHAR(200) NOT NULL,
            week_start_date TIMESTAMP NOT NULL,
            week_end_date TIMESTAMP NOT NULL,
            report_date TIMESTAMP NOT NULL,
            work_summary TEXT,
            work_content TEXT,
            next_week_plan TEXT,
            issues TEXT,
            suggestions TEXT,
            images TEXT,
            manager_signature TEXT,
            manager_sign_time TIMESTAMP,
            status VARCHAR(20) DEFAULT 'draft',
            approved_by VARCHAR(100),
            approved_at TIMESTAMP,
            reject_reason VARCHAR(500),
            created_by VARCHAR(100),
            is_deleted BIGINT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            CONSTRAINT fk_weekly_report_project FOREIGN KEY (project_id) 
                REFERENCES project_info(project_id) ON DELETE CASCADE
        );

        -- 添加表注释
        COMMENT ON TABLE weekly_report IS '维保周报表';
        COMMENT ON COLUMN weekly_report.id IS '主键ID';
        COMMENT ON COLUMN weekly_report.report_id IS '周报编号';
        COMMENT ON COLUMN weekly_report.project_id IS '项目编号';
        COMMENT ON COLUMN weekly_report.project_name IS '项目名称';
        COMMENT ON COLUMN weekly_report.week_start_date IS '周开始日期';
        COMMENT ON COLUMN weekly_report.week_end_date IS '周结束日期';
        COMMENT ON COLUMN weekly_report.report_date IS '填报日期';
        COMMENT ON COLUMN weekly_report.work_summary IS '本周工作总结';
        COMMENT ON COLUMN weekly_report.work_content IS '具体工作内容JSON数组';
        COMMENT ON COLUMN weekly_report.next_week_plan IS '下周工作计划';
        COMMENT ON COLUMN weekly_report.issues IS '存在问题';
        COMMENT ON COLUMN weekly_report.suggestions IS '建议措施';
        COMMENT ON COLUMN weekly_report.images IS '现场照片JSON数组';
        COMMENT ON COLUMN weekly_report.manager_signature IS '部门经理签字图片';
        COMMENT ON COLUMN weekly_report.manager_sign_time IS '部门经理签字时间';
        COMMENT ON COLUMN weekly_report.status IS '状态: draft草稿/submitted已提交/approved已审核/rejected已退回';
        COMMENT ON COLUMN weekly_report.approved_by IS '审核人';
        COMMENT ON COLUMN weekly_report.approved_at IS '审核时间';
        COMMENT ON COLUMN weekly_report.reject_reason IS '退回原因';
        COMMENT ON COLUMN weekly_report.created_by IS '创建人';
        COMMENT ON COLUMN weekly_report.is_deleted IS '是否删除: 0否/1是';
        COMMENT ON COLUMN weekly_report.created_at IS '创建时间';
        COMMENT ON COLUMN weekly_report.updated_at IS '更新时间';

        -- 创建索引
        CREATE INDEX idx_weekly_report_id ON weekly_report(report_id);
        CREATE INDEX idx_weekly_report_project_id ON weekly_report(project_id);
        CREATE INDEX idx_weekly_report_project_name ON weekly_report(project_name);
        CREATE INDEX idx_weekly_report_week_start ON weekly_report(week_start_date);
        CREATE INDEX idx_weekly_report_week_end ON weekly_report(week_end_date);
        CREATE INDEX idx_weekly_report_status ON weekly_report(status);
        CREATE INDEX idx_weekly_report_created_by ON weekly_report(created_by);

        RAISE NOTICE 'weekly_report表创建成功';
    ELSE
        RAISE NOTICE 'weekly_report表已存在，跳过创建';
    END IF;
END $$;
