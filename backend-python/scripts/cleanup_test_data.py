"""
删除测试数据
"""
import paramiko

server_host = "8.153.93.123"
server_user = "root"
server_password = "Lily421020"

python_script = '''
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
    cur.execute("DELETE FROM maintenance_log WHERE work_content = '测试不传项目名称'")
    conn.commit()
    print(f"Deleted {cur.rowcount} test records")
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
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
