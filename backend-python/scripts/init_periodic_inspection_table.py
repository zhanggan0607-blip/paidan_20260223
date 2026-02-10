import psycopg2

print("=" * 80)
print("初始化 periodic_inspection 表")
print("=" * 80)

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="tq",
        user="postgres",
        password="123456"
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("\n✅ 数据库连接成功\n")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS periodic_inspection (
            id BIGSERIAL PRIMARY KEY,
            inspection_id VARCHAR(50) UNIQUE NOT NULL,
            project_id VARCHAR(50) NOT NULL,
            project_name VARCHAR(200) NOT NULL,
            plan_start_date TIMESTAMP NOT NULL,
            plan_end_date TIMESTAMP NOT NULL,
            client_name VARCHAR(100),
            maintenance_personnel VARCHAR(100),
            status VARCHAR(20) NOT NULL DEFAULT '未进行',
            remarks VARCHAR(500),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    print("✅ periodic_inspection 表创建成功\n")
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_periodic_inspection_inspection_id ON periodic_inspection(inspection_id);
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_periodic_inspection_project_id ON periodic_inspection(project_id);
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_periodic_inspection_project_name ON periodic_inspection(project_name);
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_periodic_inspection_client_name ON periodic_inspection(client_name);
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_periodic_inspection_status ON periodic_inspection(status);
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_periodic_inspection_plan_start_date ON periodic_inspection(plan_start_date);
    """)
    
    print("✅ 索引创建成功\n")
    
    cursor.execute("""
        COMMENT ON TABLE periodic_inspection IS '定期巡检单表';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN periodic_inspection.id IS '主键ID';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN periodic_inspection.inspection_id IS '巡检单编号';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN periodic_inspection.project_id IS '项目编号';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN periodic_inspection.project_name IS '项目名称';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN periodic_inspection.plan_start_date IS '计划开始日期';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN periodic_inspection.plan_end_date IS '计划结束日期';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN periodic_inspection.client_name IS '客户单位';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN periodic_inspection.maintenance_personnel IS '运维人员';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN periodic_inspection.status IS '状态';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN periodic_inspection.remarks IS '备注';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN periodic_inspection.created_at IS '创建时间';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN periodic_inspection.updated_at IS '更新时间';
    """)
    
    print("✅ 表注释添加成功\n")
    
    cursor.close()
    conn.close()
    
    print("=" * 80)
    print("✅ periodic_inspection 表初始化完成！")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
