import psycopg2

print("=" * 80)
print("项目功能验证")
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
    
    print("1. 验证数据库表...")
    tables_to_check = [
        'project_info',
        'maintenance_plan',
        'personnel',
        'periodic_inspection',
        'inspection_item'
    ]
    
    for table in tables_to_check:
        cursor.execute(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = '{table}'
            );
        """)
        exists = cursor.fetchone()[0]
        if exists:
            print(f"   ✅ 表 '{table}' 存在")
        else:
            print(f"   ❌ 表 '{table}' 不存在")
    
    print("\n2. 验证表结构...")
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'personnel'
        ORDER BY ordinal_position;
    """)
    columns = cursor.fetchall()
    expected_columns = ['id', 'employee_id', 'name', 'gender', 'age', 'phone', 'email', 'department', 'position', 'role', 'status', 'address', 'remarks', 'created_at', 'updated_at']
    actual_columns = [col[0] for col in columns]
    
    for col in expected_columns:
        if col in actual_columns:
            print(f"   ✅ 列 '{col}' 存在")
        else:
            print(f"   ❌ 列 '{col}' 不存在")
    
    print("\n3. 验证索引...")
    cursor.execute("""
        SELECT indexname 
        FROM pg_indexes 
        WHERE tablename = 'personnel';
    """)
    indexes = cursor.fetchall()
    expected_indexes = ['personnel_pkey', 'idx_personnel_employee_id', 'idx_personnel_name', 'idx_personnel_department', 'idx_personnel_role', 'idx_personnel_status']
    actual_indexes = [idx[0] for idx in indexes]
    
    for idx in expected_indexes:
        if idx in actual_indexes:
            print(f"   ✅ 索引 '{idx}' 存在")
        else:
            print(f"   ❌ 索引 '{idx}' 不存在")
    
    print("\n4. 验证数据完整性...")
    cursor.execute("SELECT COUNT(*) FROM project_info;")
    project_count = cursor.fetchone()[0]
    print(f"   项目信息记录数: {project_count}")
    
    cursor.execute("SELECT COUNT(*) FROM maintenance_plan;")
    plan_count = cursor.fetchone()[0]
    print(f"   维保计划记录数: {plan_count}")
    
    cursor.execute("SELECT COUNT(*) FROM personnel;")
    personnel_count = cursor.fetchone()[0]
    print(f"   人员记录数: {personnel_count}")
    
    cursor.execute("SELECT COUNT(*) FROM periodic_inspection;")
    inspection_count = cursor.fetchone()[0]
    print(f"   定期巡检单记录数: {inspection_count}")
    
    cursor.execute("SELECT COUNT(*) FROM inspection_item;")
    item_count = cursor.fetchone()[0]
    print(f"   巡检事项记录数: {item_count}")
    
    print("\n5. 验证角色数据...")
    cursor.execute("SELECT DISTINCT role FROM personnel;")
    roles = cursor.fetchall()
    print(f"   现有角色: {[role[0] for role in roles]}")
    
    print("\n" + "=" * 80)
    print("✅ 数据库验证完成！")
    print("=" * 80)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
