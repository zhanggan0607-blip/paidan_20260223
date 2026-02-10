import psycopg2
from datetime import datetime
import sys

def check_database():
    """检查PostgreSQL数据库中的project_info表数据"""
    
    print("\n" + "="*80)
    print("🔍 PostgreSQL数据库检查工具")
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
        print("🔄 [步骤1] 连接数据库...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        print("✅ [步骤1] 数据库连接成功\n")
        
        # 检查表是否存在
        print("🔄 [步骤2] 检查project_info表是否存在...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'project_info'
        """)
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ [步骤2] project_info表存在\n")
        else:
            print("❌ [步骤2] project_info表不存在！\n")
            return
        
        # 检查表结构
        print("🔄 [步骤3] 检查表结构...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'project_info'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        
        print("📋 [表结构]:")
        for col in columns:
            print(f"   - {col[0]}: {col[1]} (nullable: {col[2]})")
        print()
        
        # 检查记录总数
        print("🔄 [步骤4] 检查记录总数...")
        cursor.execute("SELECT COUNT(*) FROM project_info")
        total_count = cursor.fetchone()[0]
        print(f"📊 [记录总数] {total_count} 条\n")
        
        if total_count == 0:
            print("⚠️  [警告] 表中没有数据！\n")
        else:
            # 获取所有记录
            print("🔄 [步骤5] 获取所有记录...")
            cursor.execute("""
                SELECT id, project_id, project_name, completion_date, 
                       maintenance_end_date, maintenance_period, client_name, 
                       address, project_abbr, client_contact, 
                       client_contact_position, client_contact_info, 
                       created_at, updated_at
                FROM project_info
                ORDER BY created_at DESC
            """)
            records = cursor.fetchall()
            
            print(f"✅ [步骤5] 获取到 {len(records)} 条记录\n")
            
            # 显示记录详情
            print("📋 [记录详情]:")
            print("-" * 80)
            
            for i, record in enumerate(records, 1):
                print(f"\n记录 #{i}:")
                print(f"   ID: {record[0]}")
                print(f"   项目编号: {record[1]}")
                print(f"   项目名称: {record[2]}")
                print(f"   开始日期: {record[3]}")
                print(f"   结束日期: {record[4]}")
                print(f"   维保周期: {record[5]}")
                print(f"   客户单位: {record[6]}")
                print(f"   地址: {record[7]}")
                print(f"   项目简称: {record[8]}")
                print(f"   客户联系人: {record[9]}")
                print(f"   联系人职位: {record[10]}")
                print(f"   联系方式: {record[11]}")
                print(f"   创建时间: {record[12]}")
                print(f"   更新时间: {record[13]}")
            
            print("\n" + "-" * 80)
        
        # 检查最新记录
        if total_count > 0:
            print("\n🔄 [步骤6] 检查最新记录...")
            cursor.execute("""
                SELECT id, project_id, project_name, created_at
                FROM project_info
                ORDER BY created_at DESC
                LIMIT 5
            """)
            latest_records = cursor.fetchall()
            
            print(f"📊 [最新5条记录]:")
            for i, record in enumerate(latest_records, 1):
                print(f"   {i}. ID={record[0]}, project_id={record[1]}, project_name={record[2]}, created_at={record[3]}")
            print()
        
        # 测试插入一条数据
        print("🔄 [步骤7] 测试插入数据...")
        test_project_id = f"TEST_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        test_data = {
            'project_id': test_project_id,
            'project_name': '测试项目',
            'completion_date': datetime.now(),
            'maintenance_end_date': datetime.now(),
            'maintenance_period': '每月',
            'client_name': '测试客户',
            'address': '测试地址',
            'project_abbr': 'TEST',
            'client_contact': '测试联系人',
            'client_contact_position': '经理',
            'client_contact_info': '13800138000'
        }
        
        try:
            cursor.execute("""
                INSERT INTO project_info (
                    project_id, project_name, completion_date, maintenance_end_date,
                    maintenance_period, client_name, address, project_abbr,
                    client_contact, client_contact_position, client_contact_info
                ) VALUES (
                    %(project_id)s, %(project_name)s, %(completion_date)s, %(maintenance_end_date)s,
                    %(maintenance_period)s, %(client_name)s, %(address)s, %(project_abbr)s,
                    %(client_contact)s, %(client_contact_position)s, %(client_contact_info)s
                )
            """, test_data)
            conn.commit()
            print(f"✅ [步骤7] 测试插入成功: project_id={test_project_id}\n")
            
            # 验证插入的数据
            cursor.execute("SELECT * FROM project_info WHERE project_id = %s", (test_project_id,))
            inserted_record = cursor.fetchone()
            
            if inserted_record:
                print("✅ [验证] 插入的数据已存在于数据库中\n")
            else:
                print("❌ [验证] 插入的数据未在数据库中找到！\n")
            
            # 清理测试数据
            print("🔄 [清理] 删除测试数据...")
            cursor.execute("DELETE FROM project_info WHERE project_id = %s", (test_project_id,))
            conn.commit()
            print(f"✅ [清理] 测试数据已删除: project_id={test_project_id}\n")
            
        except Exception as e:
            print(f"❌ [步骤7] 测试插入失败: {str(e)}\n")
            conn.rollback()
        
        # 关闭连接
        cursor.close()
        conn.close()
        print("✅ [完成] 数据库连接已关闭\n")
        
    except psycopg2.Error as e:
        print(f"❌ [数据库错误] {str(e)}\n")
        sys.exit(1)
    except Exception as e:
        print(f"❌ [未知错误] {str(e)}\n")
        sys.exit(1)
    
    print("="*80)
    print("✅ 检查完成！")
    print("="*80 + "\n")

if __name__ == "__main__":
    check_database()