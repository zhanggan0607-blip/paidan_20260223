import psycopg2
from psycopg2 import sql
import sys

print("=" * 80)
print("Maintenance Plan 数据库表检查")
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
    
    print("=" * 80)
    print("1. 检查表是否存在")
    print("=" * 80)
    
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'maintenance_plan'
    """)
    
    table_exists = cursor.fetchone()
    
    if table_exists:
        print(f"✅ 表 'maintenance_plan' 存在\n")
    else:
        print(f"❌ 表 'maintenance_plan' 不存在\n")
        sys.exit(1)
    
    print("=" * 80)
    print("2. 检查表结构")
    print("=" * 80)
    
    cursor.execute("""
        SELECT 
            column_name,
            data_type,
            character_maximum_length,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'maintenance_plan'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    print(f"表中共有 {len(columns)} 个字段:\n")
    
    for i, (col_name, data_type, max_length, nullable, default) in enumerate(columns, 1):
        nullable_str = "可空" if nullable == "YES" else "非空"
        default_str = f", 默认值: {default}" if default else ""
        max_len_str = f"({max_length})" if max_length else ""
        print(f"  {i:2d}. {col_name:30s} {data_type}{max_len_str:15s} - {nullable_str}{default_str}")
    
    print()
    
    print("=" * 80)
    print("3. 检查索引")
    print("=" * 80)
    
    cursor.execute("""
        SELECT 
            indexname,
            indexdef
        FROM pg_indexes
        WHERE tablename = 'maintenance_plan'
        AND schemaname = 'public'
    """)
    
    indexes = cursor.fetchall()
    print(f"表中共有 {len(indexes)} 个索引:\n")
    
    for i, (index_name, index_def) in enumerate(indexes, 1):
        print(f"  {i}. {index_name}")
        print(f"     {index_def}")
        print()
    
    print("=" * 80)
    print("4. 检查表中的记录数")
    print("=" * 80)
    
    cursor.execute("SELECT COUNT(*) FROM maintenance_plan")
    count = cursor.fetchone()[0]
    
    print(f"表中当前记录数: {count}\n")
    
    if count > 0:
        print("最近插入的5条记录:\n")
        cursor.execute("""
            SELECT * FROM maintenance_plan 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        rows = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description]
        
        print("字段:", ", ".join(col_names))
        print("-" * 200)
        
        for row in rows:
            print(", ".join(str(v) if v is not None else "NULL" for v in row))
            print()
    else:
        print("⚠️  表中没有任何记录\n")
    
    print("=" * 80)
    print("5. 检查数据库权限")
    print("=" * 80)
    
    cursor.execute("""
        SELECT 
            grantee,
            privilege_type,
            is_grantable
        FROM information_schema.role_table_grants
        WHERE table_schema = 'public'
        AND table_name = 'maintenance_plan'
        ORDER BY grantee, privilege_type
    """)
    
    grants = cursor.fetchall()
    print(f"表权限设置:\n")
    
    for grantee, privilege, is_grantable in grants:
        grantable_str = " (可授予)" if is_grantable == "YES" else ""
        print(f"  用户: {grantee:20s} 权限: {privilege:15s}{grantable_str}")
    
    print()
    
    print("=" * 80)
    print("6. 检查表创建时间")
    print("=" * 80)
    
    cursor.execute("""
        SELECT 
            pg_class.reltuples::bigint AS estimated_rows,
            pg_class.relpages AS pages,
            pg_size_pretty(pg_total_relation_size('maintenance_plan')) AS total_size
        FROM pg_class
        WHERE pg_class.relname = 'maintenance_plan'
    """)
    
    stats = cursor.fetchone()
    if stats:
        estimated_rows, pages, total_size = stats
        print(f"估计行数: {estimated_rows}")
        print(f"页面数: {pages}")
        print(f"总大小: {total_size}\n")
    
    print("=" * 80)
    print("7. 检查约束")
    print("=" * 80)
    
    cursor.execute("""
        SELECT 
            constraint_name,
            constraint_type
        FROM information_schema.table_constraints
        WHERE table_schema = 'public'
        AND table_name = 'maintenance_plan'
        ORDER BY constraint_type, constraint_name
    """)
    
    constraints = cursor.fetchall()
    print(f"表约束:\n")
    
    for constraint_name, constraint_type in constraints:
        print(f"  {constraint_type:15s} - {constraint_name}")
    
    print()
    
    print("=" * 80)
    print("8. 检查序列")
    print("=" * 80)
    
    cursor.execute("""
        SELECT 
            sequence_name
        FROM information_schema.sequences
        WHERE sequence_schema = 'public'
        AND sequence_name LIKE '%maintenance_plan%'
    """)
    
    sequences = cursor.fetchall()
    
    if sequences:
        print(f"相关序列:\n")
        
        for seq in sequences:
            seq_name = seq[0]
            print(f"  序列名: {seq_name}")
            
            try:
                cursor.execute(f"SELECT last_value FROM {seq_name}")
                last_value = cursor.fetchone()[0]
                print(f"    当前值: {last_value}")
            except Exception as e:
                print(f"    当前值: 无法获取 ({e})")
            
            try:
                cursor.execute(f"SELECT start_value FROM {seq_name}")
                start_value = cursor.fetchone()[0]
                print(f"    起始值: {start_value}")
            except Exception as e:
                print(f"    起始值: 无法获取 ({e})")
            
            print()
    else:
        print("没有找到相关序列\n")
    
    cursor.close()
    conn.close()
    
    print("=" * 80)
    print("检查完成")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
