import psycopg2

print("=" * 80)
print("检查 maintenance_plan 表中的数据")
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
    
    cursor.execute("SELECT COUNT(*) FROM maintenance_plan")
    count = cursor.fetchone()[0]
    
    print(f"表中记录数: {count}\n")
    
    if count > 0:
        print("=" * 80)
        print("表中的数据:")
        print("=" * 80)
        
        cursor.execute("""
            SELECT id, plan_id, plan_name, project_id, plan_type, 
                   equipment_name, plan_status, execution_status, completion_rate
            FROM maintenance_plan
            ORDER BY id
        """)
        
        records = cursor.fetchall()
        
        print(f"\n{'ID':<5} {'计划编号':<15} {'计划名称':<20} {'项目编号':<10} {'计划类型':<10} {'设备名称':<15} {'计划状态':<10} {'执行状态':<10} {'完成率':<10}")
        print("-" * 115)
        
        for record in records:
            print(f"{record[0]:<5} {record[1]:<15} {record[2]:<20} {record[3]:<10} {record[4]:<10} {record[5]:<15} {record[6]:<10} {record[7]:<10} {record[8]:<10}")
        
        print(f"\n总计: {len(records)} 条记录")
    else:
        print("⚠️  表中确实没有数据！")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
