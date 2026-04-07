"""
执行数据库迁移脚本 - 修改 maintenance_log 表的 project_id 和 project_name 字段为可空
"""
import paramiko

server_host = "8.153.93.123"
server_user = "root"
server_password = "Lily421020"

migration_sql = """
ALTER TABLE maintenance_log 
ALTER COLUMN project_id DROP NOT NULL;

ALTER TABLE maintenance_log 
ALTER COLUMN project_name DROP NOT NULL;
"""

python_script = f'''
import psycopg2

conn = psycopg2.connect(
    host="pgm-uf6cml154nbjz51y6o.pg.rds.aliyuncs.com",
    port=5432,
    database="tq",
    user="zhanggan",
    password="Lily421020#"
)
cur = conn.cursor()

try:
    cur.execute("""{migration_sql}""")
    conn.commit()
    print("Migration completed successfully!")
except Exception as e:
    conn.rollback()
    print(f"Migration failed: {{e}}")
finally:
    cur.close()
    conn.close()
'''

cmd = f'''cat << 'EOF' | podman exec -i sstcp-backend python
{python_script}
EOF'''

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server_host, username=server_user, password=server_password)
    
    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode()
    error = stderr.read().decode()
    
    print("Output:", output)
    if error:
        print("Error:", error)
    
    ssh.close()
except Exception as e:
    print(f"SSH connection error: {e}")
