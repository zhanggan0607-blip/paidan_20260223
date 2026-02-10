import psycopg2

print("=" * 80)
print("检查所有数据库")
print("=" * 80)

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="postgres",
        user="postgres",
        password="123456"
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("\n✅ 连接到 postgres 数据库成功\n")
    
    cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname")
    databases = cursor.fetchall()
    
    print("=" * 80)
    print("所有数据库列表:")
    print("=" * 80)
    
    for i, (db_name,) in enumerate(databases, 1):
        print(f"{i}. {db_name}")
    
    print("\n" + "=" * 80)
    print("检查每个数据库中的 maintenance_plan 表")
    print("=" * 80)
    
    for db_name, in databases:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {db_name}.information_schema.tables WHERE table_name = 'maintenance_plan'")
            table_exists = cursor.fetchone()[0]
            
            if table_exists > 0:
                cursor.execute(f"SELECT COUNT(*) FROM {db_name}.public.maintenance_plan")
                count = cursor.fetchone()[0]
                print(f"\n✅ 数据库 '{db_name}' 中有 maintenance_plan 表，记录数: {count}")
            else:
                print(f"\n⚠️  数据库 '{db_name}' 中没有 maintenance_plan 表")
                
        except Exception as e:
            print(f"\n❌ 无法检查数据库 '{db_name}': {e}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("检查完成")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
