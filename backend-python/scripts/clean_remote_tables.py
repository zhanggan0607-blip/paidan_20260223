"""
通过SSH远程清理线上服务器数据库（通过后端容器）
清除备品备件、维修工具、临时维修工单、零星用工单的所有数据
"""
import paramiko

SERVER_IP = "8.153.93.123"
SSH_USER = "root"
SSH_PASSWORD = "Lily421020"


def main():
    """
    主函数
    """
    print("\n" + "=" * 60)
    print("警告: 此操作将清除线上服务器数据库以下表的所有数据:")
    print("  - 备品备件库存、入库、领用")
    print("  - 维修工具库存、入库、领用")
    print("  - 临时维修工单")
    print("  - 零星用工单及施工人员信息")
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
    
    tables_to_clean = [
        ("spot_work_worker", "施工人员信息"),
        ("spot_work", "零星用工单"),
        ("temporary_repair", "临时维修工单"),
        ("spare_parts_usage", "备品备件领用"),
        ("spare_parts_inbound", "备品备件入库"),
        ("spare_parts_stock", "备品备件库存"),
        ("repair_tools_issue", "维修工具领用"),
        ("repair_tools_inbound", "维修工具入库"),
        ("repair_tools_stock", "维修工具库存"),
    ]
    
    print("\n" + "=" * 60)
    print("开始清理数据库表数据...")
    print("=" * 60)
    
    for table_name, table_desc in tables_to_clean:
        count_cmd = f'''docker exec sstcp-backend python -c "
import psycopg2
conn = psycopg2.connect(host='host.docker.internal', port=5432, database='tq', user='postgres', password='123456')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM {table_name}')
print(cur.fetchone()[0])
cur.close()
conn.close()
"'''
        stdin, stdout, stderr = client.exec_command(count_cmd, timeout=30)
        count_str = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8')
        
        if error and 'Error' in error:
            print(f"[错误] 获取 {table_name} 数量失败: {error[:300]}")
            continue
            
        count = int(count_str) if count_str else 0
        
        if count > 0:
            delete_cmd = f'''docker exec sstcp-backend python -c "
import psycopg2
conn = psycopg2.connect(host='host.docker.internal', port=5432, database='tq', user='postgres', password='123456')
conn.autocommit = True
cur = conn.cursor()
cur.execute('DELETE FROM {table_name}')
print('OK')
cur.close()
conn.close()
"'''
            stdin, stdout, stderr = client.exec_command(delete_cmd, timeout=30)
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            if error and 'Error' in error:
                print(f"[错误] 清理 {table_desc}({table_name}) 失败: {error[:300]}")
            else:
                print(f"[已清除] {table_desc}({table_name}): {count} 条记录")
        else:
            print(f"[跳过] {table_desc}({table_name}): 无数据")
    
    print("=" * 60)
    print("数据清理完成!")
    print("=" * 60)
    
    print("\n验证清理结果:")
    print("-" * 40)
    
    for table_name, table_desc in tables_to_clean:
        count_cmd = f'''docker exec sstcp-backend python -c "
import psycopg2
conn = psycopg2.connect(host='host.docker.internal', port=5432, database='tq', user='postgres', password='123456')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM {table_name}')
print(cur.fetchone()[0])
cur.close()
conn.close()
"'''
        stdin, stdout, stderr = client.exec_command(count_cmd, timeout=30)
        count_str = stdout.read().decode('utf-8').strip()
        count = int(count_str) if count_str else 0
        status = "✓ 已清空" if count == 0 else f"✗ 剩余 {count} 条"
        print(f"{table_name}: {status}")
    
    print("-" * 40)
    
    client.close()
    print("\n完成!")


if __name__ == "__main__":
    main()
