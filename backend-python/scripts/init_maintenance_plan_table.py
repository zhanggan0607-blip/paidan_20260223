import psycopg2
from datetime import datetime


def create_maintenance_plan_table():
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'tq',
        'user': 'postgres',
        'password': '123456'
    }
    
    conn = None
    try:
        print("🔗 正在连接数据库...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        print("📋 正在创建 maintenance_plan 表...")
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS maintenance_plan (
            id BIGSERIAL PRIMARY KEY,
            plan_id VARCHAR(50) NOT NULL UNIQUE,
            plan_name VARCHAR(200) NOT NULL,
            project_id VARCHAR(50) NOT NULL,
            plan_type VARCHAR(20) NOT NULL,
            equipment_id VARCHAR(50) NOT NULL,
            equipment_name VARCHAR(200) NOT NULL,
            equipment_model VARCHAR(100),
            equipment_location VARCHAR(200),
            plan_start_date TIMESTAMP NOT NULL,
            plan_end_date TIMESTAMP NOT NULL,
            execution_date TIMESTAMP,
            next_maintenance_date TIMESTAMP,
            responsible_person VARCHAR(50) NOT NULL,
            responsible_department VARCHAR(100),
            contact_info VARCHAR(50),
            maintenance_content TEXT NOT NULL,
            maintenance_requirements TEXT,
            maintenance_standard TEXT,
            plan_status VARCHAR(20) NOT NULL,
            execution_status VARCHAR(20) NOT NULL,
            completion_rate INTEGER DEFAULT 0,
            remarks TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        
        COMMENT ON TABLE maintenance_plan IS '维保计划表';
        COMMENT ON COLUMN maintenance_plan.id IS '主键ID';
        COMMENT ON COLUMN maintenance_plan.plan_id IS '计划编号';
        COMMENT ON COLUMN maintenance_plan.plan_name IS '计划名称';
        COMMENT ON COLUMN maintenance_plan.project_id IS '关联项目编号';
        COMMENT ON COLUMN maintenance_plan.plan_type IS '计划类型';
        COMMENT ON COLUMN maintenance_plan.equipment_id IS '设备编号';
        COMMENT ON COLUMN maintenance_plan.equipment_name IS '设备名称';
        COMMENT ON COLUMN maintenance_plan.equipment_model IS '设备型号';
        COMMENT ON COLUMN maintenance_plan.equipment_location IS '设备位置';
        COMMENT ON COLUMN maintenance_plan.plan_start_date IS '计划开始日期';
        COMMENT ON COLUMN maintenance_plan.plan_end_date IS '计划结束日期';
        COMMENT ON COLUMN maintenance_plan.execution_date IS '执行日期';
        COMMENT ON COLUMN maintenance_plan.next_maintenance_date IS '下次维保日期';
        COMMENT ON COLUMN maintenance_plan.responsible_person IS '负责人';
        COMMENT ON COLUMN maintenance_plan.responsible_department IS '负责部门';
        COMMENT ON COLUMN maintenance_plan.contact_info IS '联系方式';
        COMMENT ON COLUMN maintenance_plan.maintenance_content IS '维保内容';
        COMMENT ON COLUMN maintenance_plan.maintenance_requirements IS '维保要求';
        COMMENT ON COLUMN maintenance_plan.maintenance_standard IS '维保标准';
        COMMENT ON COLUMN maintenance_plan.plan_status IS '计划状态';
        COMMENT ON COLUMN maintenance_plan.execution_status IS '执行状态';
        COMMENT ON COLUMN maintenance_plan.completion_rate IS '完成率';
        COMMENT ON COLUMN maintenance_plan.remarks IS '备注';
        COMMENT ON COLUMN maintenance_plan.created_at IS '创建时间';
        COMMENT ON COLUMN maintenance_plan.updated_at IS '更新时间';
        """
        
        cursor.execute(create_table_sql)
        conn.commit()
        
        print("📊 正在创建索引...")
        
        create_indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_plan_id ON maintenance_plan(plan_id);",
            "CREATE INDEX IF NOT EXISTS idx_project_id ON maintenance_plan(project_id);",
            "CREATE INDEX IF NOT EXISTS idx_equipment_id ON maintenance_plan(equipment_id);",
            "CREATE INDEX IF NOT EXISTS idx_plan_status ON maintenance_plan(plan_status);",
            "CREATE INDEX IF NOT EXISTS idx_execution_status ON maintenance_plan(execution_status);",
            "CREATE INDEX IF NOT EXISTS idx_execution_date ON maintenance_plan(execution_date);"
        ]
        
        for index_sql in create_indexes_sql:
            cursor.execute(index_sql)
        
        conn.commit()
        
        print("✅ maintenance_plan 表创建成功！")
        print("\n📋 表结构信息:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'maintenance_plan'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print(f"\n{'字段名':<25} {'数据类型':<20} {'可空':<10} {'默认值':<20}")
        print("-" * 75)
        for col in columns:
            col_name, data_type, is_nullable, default_val = col
            nullable = "YES" if is_nullable == "YES" else "NO"
            default = str(default_val) if default_val else ""
            print(f"{col_name:<25} {data_type:<20} {nullable:<10} {default:<20}")
        
        print(f"\n📊 总计: {len(columns)} 个字段")
        
    except Exception as e:
        print(f"❌ 创建表失败: {str(e)}")
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()
            print("🔌 数据库连接已关闭")


def verify_table():
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'tq',
        'user': 'postgres',
        'password': '123456'
    }
    
    try:
        print("\n🔍 验证表结构...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM maintenance_plan;")
        count = cursor.fetchone()[0]
        print(f"📊 当前记录数: {count}")
        
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'maintenance_plan';")
        exists = cursor.fetchone()[0]
        
        if exists:
            print("✅ maintenance_plan 表已存在")
        else:
            print("❌ maintenance_plan 表不存在")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 验证失败: {str(e)}")


if __name__ == "__main__":
    print("=" * 60)
    print("维保计划表初始化脚本")
    print("=" * 60)
    
    try:
        create_maintenance_plan_table()
        verify_table()
        print("\n" + "=" * 60)
        print("初始化完成！")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 初始化失败: {str(e)}")
