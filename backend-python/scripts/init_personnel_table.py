import psycopg2

print("=" * 80)
print("初始化 personnel 表")
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
        CREATE TABLE IF NOT EXISTS personnel (
            id BIGSERIAL PRIMARY KEY,
            employee_id VARCHAR(50) UNIQUE NOT NULL,
            name VARCHAR(50) NOT NULL,
            gender VARCHAR(10) NOT NULL,
            age INTEGER,
            phone VARCHAR(20),
            email VARCHAR(100),
            department VARCHAR(100),
            position VARCHAR(100),
            role VARCHAR(20) NOT NULL DEFAULT '员工',
            status VARCHAR(20) NOT NULL DEFAULT '在职',
            address VARCHAR(200),
            remarks VARCHAR(500),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    print("✅ personnel 表创建成功\n")
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_personnel_employee_id ON personnel(employee_id);
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_personnel_name ON personnel(name);
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_personnel_department ON personnel(department);
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_personnel_status ON personnel(status);
    """)
    
    print("✅ 索引创建成功\n")
    
    cursor.execute("""
        COMMENT ON TABLE personnel IS '人员信息表';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN personnel.id IS '主键ID';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN personnel.employee_id IS '员工编号';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN personnel.name IS '姓名';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN personnel.gender IS '性别';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN personnel.age IS '年龄';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN personnel.phone IS '联系电话';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN personnel.email IS '邮箱';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN personnel.department IS '所属部门';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN personnel.position IS '职位';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN personnel.role IS '角色（管理员、部门经理、员工）';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN personnel.status IS '状态';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN personnel.address IS '地址';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN personnel.remarks IS '备注';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN personnel.created_at IS '创建时间';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN personnel.updated_at IS '更新时间';
    """)
    
    print("✅ 表注释添加成功\n")
    
    cursor.close()
    conn.close()
    
    print("=" * 80)
    print("✅ personnel 表初始化完成！")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
