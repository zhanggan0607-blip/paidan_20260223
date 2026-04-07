import paramiko

server_ip = '8.153.93.123'
ssh_username = 'root'
ssh_password = 'Lily421020'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(server_ip, username=ssh_username, password=ssh_password, timeout=30)
    print(f"已连接到服务器 {server_ip}")
    
    python_script = '''import psycopg2
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

new_password = "lily421020"
password_hash = pwd_context.hash(new_password[:72])

conn = psycopg2.connect(host="pgm-uf6cml154nbjz51y6o.pg.rds.aliyuncs.com", port=5432, database="tq", user="zhanggan", password="Lily421020#")
cur = conn.cursor()

cur.execute("UPDATE personnel SET password_hash = %s, must_change_password = false WHERE name = %s", (password_hash, "张干"))
conn.commit()

print(f"密码已重置")
print(f"新密码哈希: {password_hash}")

cur.execute("SELECT id, name, phone FROM personnel WHERE name = %s", ("张干",))
row = cur.fetchone()
print(f"确认更新 - ID: {row[0]}, 姓名: {row[1]}, 电话: {row[2]}")

cur.close()
conn.close()
'''
    
    cmd = f'''cat << 'EOF' | podman exec -i sstcp-backend python
{python_script}
EOF'''
    
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    result = stdout.read().decode('utf-8').strip()
    error = stderr.read().decode('utf-8').strip()
    
    if error and 'DeprecationWarning' not in error:
        print(f"错误: {error}")
    if result:
        print("\n密码重置结果:")
        print("=" * 80)
        print(result)
        print("=" * 80)
        
except Exception as e:
    print(f"错误: {e}")
finally:
    client.close()
    print("\n连接已关闭")
