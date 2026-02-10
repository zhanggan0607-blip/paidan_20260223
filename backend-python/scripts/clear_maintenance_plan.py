import psycopg2

print("=" * 80)
print("清空 maintenance_plan 表并重新同步数据")
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
    
    print("\n✅ 连接到 tq 数据库成功\n")
    
    print("=" * 80)
    print("1. 检查当前数据")
    print("=" * 80)
    
    cursor.execute("SELECT COUNT(*) FROM maintenance_plan")
    count = cursor.fetchone()[0]
    print(f"\n当前记录数: {count}\n")
    
    if count > 0:
        print("=" * 80)
        print("2. 清空表数据")
        print("=" * 80)
        
        cursor.execute("DELETE FROM maintenance_plan")
        
        cursor.execute("SELECT COUNT(*) FROM maintenance_plan")
        new_count = cursor.fetchone()[0]
        
        print(f"\n✅ 表已清空，当前记录数: {new_count}\n")
        
        print("=" * 80)
        print("3. 重置序列")
        print("=" * 80)
        
        cursor.execute("ALTER SEQUENCE maintenance_plan_id_seq RESTART WITH 1")
        print("\n✅ 序列已重置\n")
        
        print("=" * 80)
        print("4. 验证结果")
        print("=" * 80)
        
        cursor.execute("SELECT COUNT(*) FROM maintenance_plan")
        final_count = cursor.fetchone()[0]
        
        print(f"\n✅ 验证完成，表中记录数: {final_count}")
        
        if final_count == 0:
            print("\n✅ 表已成功清空！")
            print("\n现在可以通过前端或API添加新数据。")
        else:
            print(f"\n⚠️  表中仍有 {final_count} 条记录")
    else:
        print("\n⚠️  表已经是空的，无需清空。")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("操作完成")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
