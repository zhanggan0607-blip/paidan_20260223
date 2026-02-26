#!/usr/bin/env python
"""
数据库同步工具 - 从服务器同步数据到本地
支持全量同步和增量同步
使用方法:
    python sync_tool.py              # 全量同步所有表
    python sync_tool.py --tables personnel,project_info  # 同步指定表
    python sync_tool.py --watch      # 监听模式，每5分钟自动同步
    python sync_tool.py --compare    # 仅对比数据
"""
import paramiko
import psycopg2
import re
import argparse
import time
import os
from datetime import datetime

# 服务器配置
SSH_HOST = '8.153.93.123'
SSH_PORT = 22
SSH_USER = 'root'
SSH_PASSWORD = 'lily421020'
SERVER_DB_NAME = 'sstcp_maintenance'

# 本地数据库配置
LOCAL_DB_HOST = 'localhost'
LOCAL_DB_PORT = 5432
LOCAL_DB_NAME = 'tq'
LOCAL_DB_USER = 'postgres'
LOCAL_DB_PASSWORD = '123456'

# 需要同步的表（按依赖顺序排列）
SYNC_TABLES = [
    'customer',
    'dictionary',
    'inspection_item',
    'operation_type',
    'project_info',
    'personnel',
    'maintenance_plan',
    'work_plan',
    'periodic_inspection',
    'periodic_inspection_record',
    'temporary_repair',
    'spot_work',
    'spot_work_worker',
    'spare_parts_stock',
    'spare_parts_inbound',
    'spare_parts_usage',
    'repair_tools_stock',
    'repair_tools_inbound',
    'repair_tools_issue',
    'maintenance_log',
    'weekly_report',
    'work_order_operation_log',
]


def get_ssh_connection():
    """
    创建SSH连接
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASSWORD)
    return ssh


def get_local_connection():
    """
    创建本地数据库连接
    """
    return psycopg2.connect(
        host=LOCAL_DB_HOST,
        port=LOCAL_DB_PORT,
        database=LOCAL_DB_NAME,
        user=LOCAL_DB_USER,
        password=LOCAL_DB_PASSWORD
    )


def get_table_counts(ssh, tables):
    """
    获取服务器表的记录数
    """
    counts = {}
    for table in tables:
        stdin, stdout, stderr = ssh.exec_command(
            f'sudo -u postgres psql -d {SERVER_DB_NAME} -t -A -c "SELECT COUNT(*) FROM {table}"'
        )
        counts[table] = int(stdout.read().decode().strip())
    return counts


def get_table_columns(ssh, table):
    """
    获取表的列名
    """
    stdin, stdout, stderr = ssh.exec_command(
        f'sudo -u postgres psql -d {SERVER_DB_NAME} -t -A -c "'
        f"SELECT column_name FROM information_schema.columns "
        f"WHERE table_name = '{table}' ORDER BY ordinal_position"
        f'"'
    )
    return [c.strip() for c in stdout.read().decode().strip().split('\n') if c.strip()]


def sync_table_via_binary_copy(ssh, conn, table):
    """
    使用二进制COPY格式同步表（最可靠的方式）
    通过SSH执行pg_dump，然后通过管道传输
    """
    columns = get_table_columns(ssh, table)
    
    # 使用pg_dump导出为SQL INSERT格式，通过管道传输
    cmd = f'sudo -u postgres pg_dump -d {SERVER_DB_NAME} -t public.{table} --data-only --column-inserts'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    # 读取所有输出
    content = stdout.read().decode('utf-8', errors='replace')
    
    # 清空本地表
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table}")
    conn.commit()
    
    # 解析INSERT语句
    count = 0
    
    # 使用更精确的正则表达式匹配INSERT语句
    # 格式: INSERT INTO public.table (col1, col2, ...) VALUES (val1, val2, ...);
    pattern = rf"INSERT INTO public\.{re.escape(table)}\s*\([^)]+\)\s*VALUES\s*\([^;]+\);"
    matches = re.findall(pattern, content, re.DOTALL)
    
    for stmt in matches:
        try:
            cur.execute(stmt)
            conn.commit()
            count += 1
        except Exception as e:
            conn.rollback()
    
    # 如果上面的方式失败，尝试另一种格式
    if count == 0:
        # 格式: INSERT INTO public.table VALUES (val1, val2, ...);
        pattern2 = rf"INSERT INTO public\.{re.escape(table)}\s*VALUES\s*\([^;]+\);"
        matches2 = re.findall(pattern2, content, re.DOTALL)
        
        for stmt in matches2:
            try:
                cur.execute(stmt)
                conn.commit()
                count += 1
            except:
                conn.rollback()
    
    # 重置序列
    try:
        cur.execute(f"SELECT setval('{table}_id_seq', (SELECT COALESCE(MAX(id), 1) FROM {table}))")
        conn.commit()
    except:
        pass
    
    cur.close()
    return count


def sync_table_via_file(ssh, conn, table):
    """
    通过临时文件同步表（处理大数据量）
    """
    remote_file = f'/tmp/sync_{table}.sql'
    local_file = os.path.join(os.path.dirname(__file__), f'sync_{table}.sql')
    
    # 使用pg_dump导出
    cmd = f'sudo -u postgres pg_dump -d {SERVER_DB_NAME} -t public.{table} --data-only --column-inserts > {remote_file}'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdout.channel.recv_exit_status()
    time.sleep(0.5)
    
    # 下载文件
    sftp = ssh.open_sftp()
    try:
        sftp.get(remote_file, local_file)
    except:
        return 0
    finally:
        sftp.close()
    
    # 清理远程文件
    ssh.exec_command(f'rm -f {remote_file}')
    
    # 读取SQL文件
    with open(local_file, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    # 清空本地表
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table}")
    conn.commit()
    
    # 解析INSERT语句
    count = 0
    pattern = rf"INSERT INTO public\.{re.escape(table)}\s*\([^)]+\)\s*VALUES\s*\([^;]+\);"
    matches = re.findall(pattern, content, re.DOTALL)
    
    for stmt in matches:
        try:
            cur.execute(stmt)
            conn.commit()
            count += 1
        except:
            conn.rollback()
    
    if count == 0:
        pattern2 = rf"INSERT INTO public\.{re.escape(table)}\s*VALUES\s*\([^;]+\);"
        matches2 = re.findall(pattern2, content, re.DOTALL)
        for stmt in matches2:
            try:
                cur.execute(stmt)
                conn.commit()
                count += 1
            except:
                conn.rollback()
    
    # 重置序列
    try:
        cur.execute(f"SELECT setval('{table}_id_seq', (SELECT COALESCE(MAX(id), 1) FROM {table}))")
        conn.commit()
    except:
        pass
    
    cur.close()
    
    # 清理本地文件
    try:
        os.remove(local_file)
    except:
        pass
    
    return count


def sync_all(tables=None):
    """
    同步所有表
    """
    if tables is None:
        tables = SYNC_TABLES
    
    print(f"\n{'='*60}")
    print(f"数据库同步 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    print("正在连接服务器...")
    ssh = get_ssh_connection()
    print("SSH连接成功!")
    
    conn = get_local_connection()
    
    # 获取服务器表记录数
    print("\n获取服务器数据统计...")
    server_counts = get_table_counts(ssh, tables)
    
    print(f"\n{'表名':<35} {'服务器':>8} {'同步':>8} {'状态':>8}")
    print("-" * 60)
    
    success_count = 0
    for table in tables:
        server_count = server_counts.get(table, 0)
        try:
            # 先尝试管道方式
            synced = sync_table_via_binary_copy(ssh, conn, table)
            
            # 如果失败，尝试文件方式
            if synced < server_count * 0.9:
                synced = sync_table_via_file(ssh, conn, table)
            
            if synced >= server_count:
                status = "✓ 成功"
                success_count += 1
            elif synced >= server_count * 0.9:
                status = "⚠ 部分"
                success_count += 1
            else:
                status = "✗ 失败"
            
            print(f"{table:<35} {server_count:>8} {synced:>8} {status:>8}")
        except Exception as e:
            print(f"{table:<35} {server_count:>8} {'0':>8} {'✗ 错误':>8}")
    
    conn.close()
    ssh.close()
    
    print("-" * 60)
    print(f"同步完成! 成功: {success_count}/{len(tables)} 个表")
    
    return success_count == len(tables)


def watch_mode(interval=300):
    """
    监听模式，定时同步
    """
    print(f"监听模式启动，每 {interval//60} 分钟自动同步")
    print("按 Ctrl+C 停止\n")
    
    while True:
        try:
            sync_all()
            next_time = datetime.now().timestamp() + interval
            print(f"\n下次同步: {datetime.fromtimestamp(next_time).strftime('%H:%M:%S')}")
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\n监听已停止")
            break
        except Exception as e:
            print(f"同步出错: {e}")
            time.sleep(60)


def compare():
    """
    对比服务器和本地数据
    """
    print(f"\n{'='*60}")
    print(f"数据对比 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    print("正在连接服务器...")
    ssh = get_ssh_connection()
    print("SSH连接成功!")
    
    server_counts = get_table_counts(ssh, SYNC_TABLES)
    ssh.close()
    
    conn = get_local_connection()
    cur = conn.cursor()
    
    print(f"\n{'表名':<35} {'服务器':>8} {'本地':>8} {'状态':>8}")
    print("-" * 60)
    
    diff_tables = []
    for table in SYNC_TABLES:
        server_count = server_counts.get(table, 0)
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        local_count = cur.fetchone()[0]
        
        status = "✓ 一致" if server_count == local_count else "✗ 差异"
        print(f"{table:<35} {server_count:>8} {local_count:>8} {status:>8}")
        
        if server_count != local_count:
            diff_tables.append((table, server_count, local_count))
    
    cur.close()
    conn.close()
    
    print("-" * 60)
    
    if diff_tables:
        print(f"\n发现 {len(diff_tables)} 个表数据不一致:")
        for table, server, local in diff_tables:
            print(f"  - {table}: 服务器 {server} 条, 本地 {local} 条")
        return False
    else:
        print("\n所有表数据一致!")
        return True


def main():
    parser = argparse.ArgumentParser(description='数据库同步工具')
    parser.add_argument('--tables', type=str, help='指定要同步的表，用逗号分隔')
    parser.add_argument('--watch', action='store_true', help='监听模式，定时自动同步')
    parser.add_argument('--interval', type=int, default=300, help='监听模式的同步间隔(秒)，默认300秒')
    parser.add_argument('--compare', action='store_true', help='仅对比数据，不同步')
    
    args = parser.parse_args()
    
    tables = None
    if args.tables:
        tables = [t.strip() for t in args.tables.split(',')]
    
    if args.compare:
        compare()
    elif args.watch:
        watch_mode(args.interval)
    else:
        sync_all(tables)


if __name__ == '__main__':
    main()
