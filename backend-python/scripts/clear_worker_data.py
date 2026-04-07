"""
清除服务器数据库中施工人员（spot_work_worker）的所有数据
"""
import paramiko

SERVER_IP = "8.153.93.123"
SSH_USER = "root"
SSH_PASSWORD = "Lily421020"


def main():
    """
    主函数 - 清除施工人员数据
    """
    print("\n" + "=" * 60)
    print("警告: 此操作将清除线上服务器数据库中施工人员的所有数据")
    print("表名: spot_work_worker (施工人员信息)")
    print("=" * 60)
    
    confirm = input("\n请输入 'YES' 确认执行清理: ")
    
    if confirm != "YES":
        print("操作已取消")
        return
    
    print("\n连接服务器...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SERVER_IP, port=22, username=SSH_USER, password=SSH_PASSWORD, timeout=60)
    print("连接成功!")
    
    table_name = "spot_work_worker"
    table_desc = "施工人员信息"
    
    print("\n" + "-" * 40)
    print(f"检查 {table_desc}({table_name}) 数据...")
    
    count_cmd = '''podman exec sstcp-backend python -c "
import psycopg2
conn = psycopg2.connect(host='host.docker.internal', port=5432, database='tq', user='postgres', password='123456')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM spot_work_worker')
print(cur.fetchone()[0])
cur.close()
conn.close()
"'''
    
    stdin, stdout, stderr = client.exec_command(count_cmd, timeout=30)
    count_str = stdout.read().decode('utf-8').strip()
    error = stderr.read().decode('utf-8')
    
    if error and 'Error' in error:
        print(f"[错误] 获取数据数量失败: {error[:500]}")
        client.close()
        return
        
    count = int(count_str) if count_str else 0
    print(f"当前 {table_desc} 数量: {count} 条")
    
    if count > 0:
        print(f"\n正在清除 {table_desc} 数据...")
        
        delete_cmd = '''podman exec sstcp-backend python -c "
import psycopg2
conn = psycopg2.connect(host='host.docker.internal', port=5432, database='tq', user='postgres', password='123456')
conn.autocommit = True
cur = conn.cursor()
cur.execute('DELETE FROM spot_work_worker')
print('OK')
cur.close()
conn.close()
"'''
        stdin, stdout, stderr = client.exec_command(delete_cmd, timeout=30)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        if error and 'Error' in error:
            print(f"[错误] 清理失败: {error[:500]}")
        else:
            print(f"[已清除] {table_desc}: {count} 条记录")
    else:
        print(f"[跳过] {table_desc}: 无数据")
    
    print("\n验证清理结果:")
    print("-" * 40)
    
    stdin, stdout, stderr = client.exec_command(count_cmd, timeout=30)
    count_str = stdout.read().decode('utf-8').strip()
    new_count = int(count_str) if count_str else 0
    
    if new_count == 0:
        print(f"spot_work_worker: ✓ 已清空")
    else:
        print(f"spot_work_worker: ✗ 剩余 {new_count} 条")
    
    print("-" * 40)
    
    client.close()
    print("\n完成!")


if __name__ == "__main__":
    main()
