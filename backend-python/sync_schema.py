#!/usr/bin/env python
"""
数据库结构同步脚本 - 将本地数据库结构同步到服务器
使用 subprocess 调用 ssh 和 scp 命令
"""
import psycopg2
import subprocess
import json
import os

LOCAL_DB = {
    'host': 'localhost',
    'port': 5432,
    'database': 'tq',
    'user': 'postgres',
    'password': '123456'
}

SERVER_HOST = '8.153.93.123'
SERVER_USER = 'root'
SERVER_DB = 'tq'

def get_db_structure(conn):
    """获取数据库结构"""
    cur = conn.cursor()
    
    structure = {}
    
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    tables = [row[0] for row in cur.fetchall()]
    
    for table in tables:
        cur.execute(f"""
            SELECT column_name, data_type, character_maximum_length, 
                   is_nullable, column_default, numeric_precision, numeric_scale,
                   udt_name
            FROM information_schema.columns 
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position
        """, (table,))
        columns = {}
        for row in cur.fetchall():
            col_name, data_type, char_len, nullable, default, num_prec, num_scale, udt_name = row
            columns[col_name] = {
                'data_type': data_type,
                'udt_name': udt_name,
                'char_len': char_len,
                'nullable': nullable,
                'default': default,
                'num_prec': num_prec,
                'num_scale': num_scale
            }
        
        cur.execute(f"""
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_schema = 'public' 
            AND tc.table_name = %s
            AND tc.constraint_type = 'PRIMARY KEY'
        """, (table,))
        pk_columns = [row[0] for row in cur.fetchall()]
        
        structure[table] = {
            'columns': columns,
            'pk': pk_columns
        }
    
    cur.close()
    return structure

def run_ssh_command(cmd):
    """运行SSH命令"""
    full_cmd = f'ssh -o StrictHostKeyChecking=no {SERVER_USER}@{SERVER_HOST} "{cmd}"'
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

def get_server_db_structure():
    """获取服务器数据库结构"""
    query = """
SELECT json_agg(
    json_build_object(
        'table', t.table_name,
        'columns', (
            SELECT json_object_agg(
                c.column_name,
                json_build_object(
                    'data_type', c.data_type,
                    'udt_name', c.udt_name,
                    'char_len', c.character_maximum_length,
                    'nullable', c.is_nullable,
                    'default', c.column_default,
                    'num_prec', c.numeric_precision,
                    'num_scale', c.numeric_scale
                )
            )
            FROM information_schema.columns c
            WHERE c.table_schema = 'public' AND c.table_name = t.table_name
        ),
        'pk', (
            SELECT json_agg(kcu.column_name)
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_schema = 'public' 
            AND tc.table_name = t.table_name
            AND tc.constraint_type = 'PRIMARY KEY'
        )
    )
)
FROM information_schema.tables t
WHERE t.table_schema = 'public' AND t.table_type = 'BASE TABLE'
ORDER BY t.table_name
"""
    
    cmd = f'docker exec -i sstcp-db psql -U postgres -d {SERVER_DB} -t -A -c "{query}"'
    stdout, stderr, code = run_ssh_command(cmd)
    
    if not stdout.strip():
        return {}
    
    try:
        data = json.loads(stdout.strip())
    except json.JSONDecodeError:
        print(f"解析JSON失败: {stdout[:500]}")
        return {}
    
    structure = {}
    for item in data:
        if item and item.get('table'):
            structure[item['table']] = {
                'columns': item.get('columns', {}),
                'pk': item.get('pk', [])
            }
    
    return structure

def generate_type_sql(col_info):
    """生成字段类型SQL"""
    data_type = col_info['data_type']
    char_len = col_info['char_len']
    num_prec = col_info['num_prec']
    num_scale = col_info['num_scale']
    
    if data_type == 'character varying' and char_len:
        return f'character varying({char_len})'
    elif data_type == 'character' and char_len:
        return f'character({char_len})'
    elif data_type == 'numeric' and num_prec:
        if num_scale:
            return f'numeric({num_prec},{num_scale})'
        return f'numeric({num_prec})'
    elif data_type == 'ARRAY':
        return f'{col_info["udt_name"]}[]'
    else:
        return data_type

def generate_sync_sql(local_struct, server_struct):
    """生成同步SQL语句"""
    sql_statements = []
    
    for table, table_info in local_struct.items():
        if table not in server_struct:
            col_defs = []
            for col_name, col_info in table_info['columns'].items():
                col_type = generate_type_sql(col_info)
                col_def = f'{col_name} {col_type}'
                if col_name in table_info['pk']:
                    col_def += ' PRIMARY KEY'
                if col_info['nullable'] == 'NO':
                    col_def += ' NOT NULL'
                if col_info['default']:
                    col_def += f' DEFAULT {col_info["default"]}'
                col_defs.append(f'    {col_def}')
            
            sql_statements.append(f'CREATE TABLE IF NOT EXISTS {table} (\n' + ',\n'.join(col_defs) + '\n);')
            print(f"[新建表] {table}")
        else:
            for col_name, col_info in table_info['columns'].items():
                if col_name not in server_struct[table]['columns']:
                    col_type = generate_type_sql(col_info)
                    col_def = f'{col_type}'
                    if col_info['nullable'] == 'NO':
                        col_def += ' NOT NULL'
                    if col_info['default']:
                        col_def += f' DEFAULT {col_info["default"]}'
                    
                    sql_statements.append(f'ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col_name} {col_def};')
                    print(f"[新增字段] {table}.{col_name}")
                else:
                    server_col = server_struct[table]['columns'][col_name]
                    local_type = generate_type_sql(col_info)
                    server_type = generate_type_sql(server_col)
                    
                    if local_type != server_type:
                        sql_statements.append(f'ALTER TABLE {table} ALTER COLUMN {col_name} TYPE {local_type} USING {col_name}::{local_type};')
                        print(f"[修改字段类型] {table}.{col_name}: {server_type} -> {local_type}")
    
    return sql_statements

def sync_to_server(sql_statements):
    """将结构同步到服务器"""
    schema_sql = '\n'.join(sql_statements)
    
    with open('schema_sync.sql', 'w', encoding='utf-8') as f:
        f.write(schema_sql)
    
    print("正在上传结构文件到服务器...")
    subprocess.run(f'scp -o StrictHostKeyChecking=no schema_sync.sql {SERVER_USER}@{SERVER_HOST}:/tmp/', shell=True, check=True)
    
    print("正在应用数据库结构到服务器...")
    
    run_ssh_command('docker cp /tmp/schema_sync.sql sstcp-db:/tmp/schema_sync.sql')
    cmd = f'docker exec -i sstcp-db psql -U postgres -d {SERVER_DB} -f /tmp/schema_sync.sql'
    stdout, stderr, code = run_ssh_command(cmd)
    
    print("\n执行结果:")
    print(stdout[:3000] if len(stdout) > 3000 else stdout)
    if stderr:
        print(f"错误: {stderr[:1000]}")
    
    run_ssh_command('rm -f /tmp/schema_sync.sql')
    run_ssh_command('docker exec -i sstcp-db rm -f /tmp/schema_sync.sql')
    
    print("\n数据库结构同步完成!")

def main():
    print("=" * 60)
    print("数据库结构同步工具")
    print("=" * 60)
    
    print("\n正在连接本地数据库...")
    local_conn = psycopg2.connect(
        host=LOCAL_DB['host'],
        port=LOCAL_DB['port'],
        database=LOCAL_DB['database'],
        user=LOCAL_DB['user'],
        password=LOCAL_DB['password']
    )
    
    print("正在获取本地数据库结构...")
    local_struct = get_db_structure(local_conn)
    local_conn.close()
    print(f"本地数据库有 {len(local_struct)} 个表")
    
    print("\n正在获取服务器数据库结构...")
    server_struct = get_server_db_structure()
    print(f"服务器数据库有 {len(server_struct)} 个表")
    
    print("\n正在比较数据库结构...")
    sql_statements = generate_sync_sql(local_struct, server_struct)
    
    if not sql_statements:
        print("\n数据库结构已同步，无需更新")
        return
    
    print(f"\n需要执行 {len(sql_statements)} 条SQL语句")
    
    sync_to_server(sql_statements)

if __name__ == '__main__':
    main()
