import psycopg2
from datetime import datetime
import sys

def query_database():
    """从数据库查询project_info表数据"""
    
    print("\n" + "="*80)
    print("🔍 PostgreSQL数据库查询工具")
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
        
        while True:
            print("\n" + "="*80)
            print("📋 查询选项")
            print("="*80)
            print("1. 查询所有记录")
            print("2. 查询总记录数")
            print("3. 按项目编号查询")
            print("4. 按项目名称模糊查询")
            print("5. 按客户名称模糊查询")
            print("6. 查询最新N条记录")
            print("7. 查询指定ID的记录")
            print("8. 查询指定日期范围的数据")
            print("9. 统计维保周期分布")
            print("10. 查询重复的project_id")
            print("0. 退出")
            print("="*80)
            
            choice = input("\n请选择查询选项 (0-10): ").strip()
            
            if choice == '0':
                print("\n👋 退出程序")
                break
            
            elif choice == '1':
                query_all_records(cursor)
            elif choice == '2':
                query_total_count(cursor)
            elif choice == '3':
                query_by_project_id(cursor)
            elif choice == '4':
                query_by_project_name(cursor)
            elif choice == '5':
                query_by_client_name(cursor)
            elif choice == '6':
                query_latest_records(cursor)
            elif choice == '7':
                query_by_id(cursor)
            elif choice == '8':
                query_by_date_range(cursor)
            elif choice == '9':
                query_maintenance_period_stats(cursor)
            elif choice == '10':
                query_duplicate_project_ids(cursor)
            else:
                print("\n❌ 无效的选项，请重新选择\n")
        
        # 关闭连接
        cursor.close()
        conn.close()
        print("\n✅ 数据库连接已关闭\n")
        
    except psycopg2.Error as e:
        print(f"\n❌ [数据库错误] {str(e)}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ [未知错误] {str(e)}\n")
        sys.exit(1)

def query_all_records(cursor):
    """查询所有记录"""
    print("\n🔄 [查询] 获取所有记录...\n")
    
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
    
    if records:
        print(f"✅ [结果] 找到 {len(records)} 条记录\n")
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
    else:
        print("❌ [结果] 没有找到记录\n")

def query_total_count(cursor):
    """查询总记录数"""
    print("\n🔄 [查询] 统计总记录数...\n")
    
    cursor.execute("SELECT COUNT(*) FROM project_info")
    count = cursor.fetchone()[0]
    
    print(f"📊 [结果] 总记录数: {count}\n")

def query_by_project_id(cursor):
    """按项目编号查询"""
    project_id = input("\n请输入项目编号: ").strip()
    
    if not project_id:
        print("❌ 项目编号不能为空\n")
        return
    
    print(f"\n🔄 [查询] 查询项目编号: {project_id}\n")
    
    cursor.execute(
        "SELECT * FROM project_info WHERE project_id = %s",
        (project_id,)
    )
    
    record = cursor.fetchone()
    
    if record:
        print("✅ [结果] 找到记录\n")
        print("-" * 80)
        print(f"ID: {record[0]}")
        print(f"项目编号: {record[1]}")
        print(f"项目名称: {record[2]}")
        print(f"开始日期: {record[3]}")
        print(f"结束日期: {record[4]}")
        print(f"维保周期: {record[5]}")
        print(f"客户单位: {record[6]}")
        print(f"地址: {record[7]}")
        print(f"项目简称: {record[8]}")
        print(f"客户联系人: {record[9]}")
        print(f"联系人职位: {record[10]}")
        print(f"联系方式: {record[11]}")
        print(f"创建时间: {record[12]}")
        print(f"更新时间: {record[13]}")
        print("-" * 80 + "\n")
    else:
        print(f"❌ [结果] 未找到项目编号为 {project_id} 的记录\n")

def query_by_project_name(cursor):
    """按项目名称模糊查询"""
    project_name = input("\n请输入项目名称（支持模糊查询）: ").strip()
    
    if not project_name:
        print("❌ 项目名称不能为空\n")
        return
    
    print(f"\n🔄 [查询] 查询项目名称: {project_name}\n")
    
    cursor.execute(
        "SELECT * FROM project_info WHERE project_name LIKE %s ORDER BY created_at DESC",
        (f'%{project_name}%',)
    )
    
    records = cursor.fetchall()
    
    if records:
        print(f"✅ [结果] 找到 {len(records)} 条记录\n")
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
            print(f"   创建时间: {record[12]}")
        print("\n" + "-" * 80)
    else:
        print(f"❌ [结果] 未找到包含 {project_name} 的项目\n")

def query_by_client_name(cursor):
    """按客户名称模糊查询"""
    client_name = input("\n请输入客户名称（支持模糊查询）: ").strip()
    
    if not client_name:
        print("❌ 客户名称不能为空\n")
        return
    
    print(f"\n🔄 [查询] 查询客户名称: {client_name}\n")
    
    cursor.execute(
        "SELECT * FROM project_info WHERE client_name LIKE %s ORDER BY created_at DESC",
        (f'%{client_name}%',)
    )
    
    records = cursor.fetchall()
    
    if records:
        print(f"✅ [结果] 找到 {len(records)} 条记录\n")
        print("-" * 80)
        for i, record in enumerate(records, 1):
            print(f"\n记录 #{i}:")
            print(f"   ID: {record[0]}")
            print(f"   项目编号: {record[1]}")
            print(f"   项目名称: {record[2]}")
            print(f"   客户单位: {record[6]}")
            print(f"   地址: {record[7]}")
            print(f"   创建时间: {record[12]}")
        print("\n" + "-" * 80)
    else:
        print(f"❌ [结果] 未找到包含 {client_name} 的客户\n")

def query_latest_records(cursor):
    """查询最新N条记录"""
    n = input("\n请输入要查询的记录数: ").strip()
    
    try:
        n = int(n)
        if n <= 0:
            print("❌ 记录数必须大于0\n")
            return
    except ValueError:
        print("❌ 请输入有效的数字\n")
        return
    
    print(f"\n🔄 [查询] 查询最新 {n} 条记录\n")
    
    cursor.execute("""
        SELECT * FROM project_info
        ORDER BY created_at DESC
        LIMIT %s
    """, (n,))
    
    records = cursor.fetchall()
    
    if records:
        print(f"✅ [结果] 找到 {len(records)} 条记录\n")
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
            print(f"   创建时间: {record[12]}")
        print("\n" + "-" * 80)
    else:
        print("❌ [结果] 没有找到记录\n")

def query_by_id(cursor):
    """查询指定ID的记录"""
    id_input = input("\n请输入记录ID: ").strip()
    
    try:
        id_value = int(id_input)
    except ValueError:
        print("❌ 请输入有效的数字\n")
        return
    
    print(f"\n🔄 [查询] 查询ID: {id_value}\n")
    
    cursor.execute(
        "SELECT * FROM project_info WHERE id = %s",
        (id_value,)
    )
    
    record = cursor.fetchone()
    
    if record:
        print("✅ [结果] 找到记录\n")
        print("-" * 80)
        print(f"ID: {record[0]}")
        print(f"项目编号: {record[1]}")
        print(f"项目名称: {record[2]}")
        print(f"开始日期: {record[3]}")
        print(f"结束日期: {record[4]}")
        print(f"维保周期: {record[5]}")
        print(f"客户单位: {record[6]}")
        print(f"地址: {record[7]}")
        print(f"项目简称: {record[8]}")
        print(f"客户联系人: {record[9]}")
        print(f"联系人职位: {record[10]}")
        print(f"联系方式: {record[11]}")
        print(f"创建时间: {record[12]}")
        print(f"更新时间: {record[13]}")
        print("-" * 80 + "\n")
    else:
        print(f"❌ [结果] 未找到ID为 {id_value} 的记录\n")

def query_by_date_range(cursor):
    """查询指定日期范围的数据"""
    start_date = input("\n请输入开始日期 (YYYY-MM-DD，留空则不限制): ").strip()
    end_date = input("请输入结束日期 (YYYY-MM-DD，留空则不限制): ").strip()
    
    conditions = []
    params = []
    
    if start_date:
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            conditions.append("completion_date >= %s")
            params.append(start_date)
        except ValueError:
            print("❌ 开始日期格式错误，请使用 YYYY-MM-DD 格式\n")
            return
    
    if end_date:
        try:
            datetime.strptime(end_date, '%Y-%m-%d')
            conditions.append("completion_date <= %s")
            params.append(end_date)
        except ValueError:
            print("❌ 结束日期格式错误，请使用 YYYY-MM-DD 格式\n")
            return
    
    if not conditions:
        print("❌ 请至少输入一个日期\n")
        return
    
    query = "SELECT * FROM project_info"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY created_at DESC"
    
    print(f"\n🔄 [查询] 查询日期范围: {start_date} 到 {end_date}\n")
    
    cursor.execute(query, params)
    records = cursor.fetchall()
    
    if records:
        print(f"✅ [结果] 找到 {len(records)} 条记录\n")
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
            print(f"   创建时间: {record[12]}")
        print("\n" + "-" * 80)
    else:
        print("❌ [结果] 没有找到记录\n")

def query_maintenance_period_stats(cursor):
    """统计维保周期分布"""
    print("\n🔄 [查询] 统计维保周期分布...\n")
    
    cursor.execute("""
        SELECT maintenance_period, COUNT(*) as count
        FROM project_info
        GROUP BY maintenance_period
        ORDER BY count DESC
    """)
    
    records = cursor.fetchall()
    
    if records:
        print("✅ [结果] 维保周期分布\n")
        print("-" * 80)
        print(f"{'维保周期':<20} {'数量':<10} {'占比':<10}")
        print("-" * 80)
        
        total = sum(record[1] for record in records)
        
        for record in records:
            period = record[0]
            count = record[1]
            percentage = (count / total * 100) if total > 0 else 0
            print(f"{period:<20} {count:<10} {percentage:>6.2f}%")
        
        print("-" * 80)
        print(f"总计: {total} 条记录\n")
    else:
        print("❌ [结果] 没有找到记录\n")

def query_duplicate_project_ids(cursor):
    """查询重复的project_id"""
    print("\n🔄 [查询] 检查重复的project_id...\n")
    
    cursor.execute("""
        SELECT project_id, COUNT(*) as count
        FROM project_info
        GROUP BY project_id
        HAVING COUNT(*) > 1
        ORDER BY count DESC
    """)
    
    records = cursor.fetchall()
    
    if records:
        print(f"❌ [结果] 发现 {len(records)} 个重复的project_id\n")
        print("-" * 80)
        for record in records:
            print(f"项目编号: {record[0]}, 重复次数: {record[1]}")
        print("-" * 80 + "\n")
    else:
        print("✅ [结果] 没有发现重复的project_id\n")

if __name__ == "__main__":
    query_database()