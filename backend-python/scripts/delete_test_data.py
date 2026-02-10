import psycopg2

def delete_test_data():
    """删除数据库中的测试数据"""
    
    print("\n" + "="*80)
    print("🗑️  清除测试数据工具")
    print("="*80 + "\n")
    
    # 数据库连接配置
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'tq',
        'user': 'postgres',
        'password': '123456'
    }
    
    print(f"📊 [连接配置] {db_config}\n")
    
    try:
        # 连接数据库
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        print("✅ 数据库连接成功\n")
        
        # 查询所有数据
        cursor.execute("SELECT id, project_id, project_name FROM project_info ORDER BY created_at DESC")
        all_records = cursor.fetchall()
        
        print(f"📊 [当前数据] 共 {len(all_records)} 条记录\n")
        
        if not all_records:
            print("❌ 数据库中没有数据\n")
            return
        
        # 识别测试数据
        test_patterns = ['TEST', '测试', '232323', '2313', '2323432', '1231232']
        test_records = []
        real_records = []
        
        for record in all_records:
            record_id = record[0]
            project_id = record[1]
            project_name = record[2]
            
            is_test = False
            for pattern in test_patterns:
                if pattern in project_id or pattern in project_name:
                    is_test = True
                    break
            
            if is_test:
                test_records.append(record)
            else:
                real_records.append(record)
        
        print(f"📊 [分析结果]")
        print(f"   - 测试数据: {len(test_records)} 条")
        print(f"   - 真实数据: {len(real_records)} 条\n")
        
        if test_records:
            print("📋 [将要删除的测试数据]:")
            print("-" * 80)
            for i, record in enumerate(test_records, 1):
                print(f"\n记录 #{i}:")
                print(f"   ID: {record[0]}")
                print(f"   项目编号: {record[1]}")
                print(f"   项目名称: {record[2]}")
            print("\n" + "-" * 80 + "\n")
            
            # 确认删除
            confirm = input("⚠️  确认删除这些测试数据吗？(yes/no): ").strip().lower()
            
            if confirm in ['yes', 'y']:
                # 删除测试数据
                print("\n🔄 [删除] 开始删除测试数据...\n")
                
                deleted_count = 0
                for record in test_records:
                    record_id = record[0]
                    cursor.execute("DELETE FROM project_info WHERE id = %s", (record_id,))
                    deleted_count += 1
                
                conn.commit()
                
                print(f"✅ [删除成功] 已删除 {deleted_count} 条测试数据\n")
                
                # 验证删除结果
                cursor.execute("SELECT COUNT(*) FROM project_info")
                remaining_count = cursor.fetchone()[0]
                
                print(f"📊 [验证] 剩余记录数: {remaining_count}\n")
                
                if remaining_count == len(real_records):
                    print("✅ [验证成功] 所有测试数据已删除，只保留真实数据\n")
                else:
                    print("⚠️  [警告] 删除后的记录数与预期不符\n")
                
                # 显示剩余数据
                if real_records:
                    print("📋 [剩余的真实数据]:")
                    print("-" * 80)
                    for i, record in enumerate(real_records, 1):
                        print(f"\n记录 #{i}:")
                        print(f"   ID: {record[0]}")
                        print(f"   项目编号: {record[1]}")
                        print(f"   项目名称: {record[2]}")
                    print("\n" + "-" * 80 + "\n")
                else:
                    print("❌ 数据库中没有真实数据\n")
            else:
                print("❌ [取消] 删除操作已取消\n")
        else:
            print("✅ [验证] 没有发现测试数据\n")
        
        # 关闭连接
        cursor.close()
        conn.close()
        print("\n✅ 数据库连接已关闭\n")
        
    except psycopg2.Error as e:
        print(f"\n❌ [数据库错误] {str(e)}\n")
        import sys
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ [未知错误] {str(e)}\n")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    delete_test_data()