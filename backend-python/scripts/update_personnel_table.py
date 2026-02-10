import psycopg2

def update_personnel_table():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="tq",
        user="postgres",
        password="123456"
    )
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        print("开始更新personnel表结构...")

        # 删除旧的索引
        print("删除旧索引...")
        cursor.execute("DROP INDEX IF EXISTS idx_personnel_employee_id;")
        cursor.execute("DROP INDEX IF EXISTS idx_personnel_status;")
        cursor.execute("DROP INDEX IF EXISTS idx_personnel_position;")

        # 删除旧字段
        print("删除旧字段...")
        cursor.execute("ALTER TABLE personnel DROP COLUMN IF EXISTS employee_id;")
        cursor.execute("ALTER TABLE personnel DROP COLUMN IF EXISTS age;")
        cursor.execute("ALTER TABLE personnel DROP COLUMN IF EXISTS email;")
        cursor.execute("ALTER TABLE personnel DROP COLUMN IF EXISTS position;")
        cursor.execute("ALTER TABLE personnel DROP COLUMN IF EXISTS status;")

        # 创建新索引
        print("创建新索引...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_personnel_name ON personnel(name);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_personnel_department ON personnel(department);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_personnel_role ON personnel(role);")

        # 验证表结构
        print("\n验证表结构:")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'personnel'
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        for col in columns:
            print(f"   - {col[0]}: {col[1]}")

        print("\n验证索引:")
        cursor.execute("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = 'personnel';
        """)
        indexes = cursor.fetchall()
        for idx in indexes:
            print(f"   - {idx[0]}")

        print("\n✅ personnel表结构更新成功！")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    update_personnel_table()
