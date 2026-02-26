#!/usr/bin/env python
"""
数据库同步脚本 - 从服务器同步数据到本地
使用INSERT格式导出，避免COPY命令问题
"""
import paramiko
import os
import psycopg2

SSH_HOST = '8.153.93.123'
SSH_PORT = 22
SSH_USER = 'root'
SSH_PASSWORD = 'lily421020'

SERVER_DB_NAME = 'sstcp_maintenance'

LOCAL_DB_HOST = 'localhost'
LOCAL_DB_PORT = 5432
LOCAL_DB_NAME = 'tq'
LOCAL_DB_USER = 'postgres'
LOCAL_DB_PASSWORD = '123456'

BACKUP_FILE = '/tmp/server_db_backup.sql'
LOCAL_BACKUP = os.path.join(os.path.dirname(__file__), 'server_backup.sql')

def sync_database():
    """
    通过SSH隧道同步服务器数据库到本地
    """
    print("正在连接服务器...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASSWORD)
        print("SSH连接成功!")
        
        print("正在导出服务器数据库(使用INSERT格式)...")
        
        export_cmd = f'sudo -u postgres pg_dump {SERVER_DB_NAME} --no-owner --no-acl --column-inserts -f {BACKUP_FILE}'
        stdin, stdout, stderr = ssh.exec_command(export_cmd)
        exit_status = stdout.channel.recv_exit_status()
        
        error_output = stderr.read().decode()
        if exit_status != 0:
            print(f"导出输出: {error_output}")
            if 'error' in error_output.lower() or 'fatal' in error_output.lower():
                return False
        
        print("数据库导出成功!")
        
        print("正在下载备份文件...")
        sftp = ssh.open_sftp()
        sftp.get(BACKUP_FILE, LOCAL_BACKUP)
        sftp.close()
        print(f"备份文件已下载到: {LOCAL_BACKUP}")
        
        print("正在清理服务器临时文件...")
        ssh.exec_command(f'sudo rm -f {BACKUP_FILE}')
        
        ssh.close()
        
        print("正在导入到本地数据库...")
        
        conn = psycopg2.connect(
            host=LOCAL_DB_HOST,
            port=LOCAL_DB_PORT,
            database=LOCAL_DB_NAME,
            user=LOCAL_DB_USER,
            password=LOCAL_DB_PASSWORD
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        with open(LOCAL_BACKUP, 'r', encoding='utf-8') as f:
            content = f.read()
        
        statements = []
        current = []
        
        for line in content.split('\n'):
            stripped = line.strip()
            
            if stripped.startswith('\\'):
                continue
            if stripped.startswith('--'):
                continue
            
            current.append(line)
            
            if stripped.endswith(';'):
                stmt = '\n'.join(current).strip()
                current = []
                
                if stmt and not stmt.startswith('--'):
                    statements.append(stmt)
        
        total = len(statements)
        success = 0
        errors = 0
        
        for i, stmt in enumerate(statements):
            try:
                cur.execute(stmt)
                success += 1
                if (i + 1) % 100 == 0:
                    print(f"  进度: {i+1}/{total}")
            except Exception as e:
                errors += 1
                if errors < 10:
                    print(f"  语句错误: {str(e)[:100]}")
        
        cur.close()
        conn.close()
        
        print(f"\n导入完成! 成功: {success}, 错误: {errors}")
        
        print("正在清理本地临时文件...")
        os.remove(LOCAL_BACKUP)
        
        print("\n数据库同步完成!")
        return True
        
    except Exception as e:
        print(f"同步失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            ssh.close()
        except:
            pass

if __name__ == '__main__':
    sync_database()
