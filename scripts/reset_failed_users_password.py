import paramiko
import sys

SERVER_IP = '8.153.95.31'
SERVER_PASSWORD = os.environ.get('SERVER_PASSWORD', '')

USERS_TO_RESET = [
    (24, '晋海龙'),
    (25, '张鑫'),
    (26, '贺志明'),
    (38, '金辉'),
    (42, '赵玉'),
    (43, '郑强'),
]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER_IP, username='root', password=SERVER_PASSWORD, timeout=15)

stdin, stdout, stderr = ssh.exec_command('docker ps --format "{{.Names}}" | grep backend')
container = stdout.read().decode().strip()
print(f'Backend container: {container}')

if not container:
    print('ERROR: No backend container found!')
    ssh.close()
    sys.exit(1)

user_ids = ','.join(str(uid) for uid, _ in USERS_TO_RESET)

reset_cmd = f"""docker exec {container} python -c "
import bcrypt
import psycopg2

new_password = '123456'
truncated = new_password[:72].encode('utf-8')
hashed = bcrypt.hashpw(truncated, bcrypt.gensalt()).decode('utf-8')

conn = psycopg2.connect(os.environ.get('DATABASE_URL', ''))
cur = conn.cursor()

user_ids = [{user_ids}]
for uid in user_ids:
    cur.execute('UPDATE personnel SET password_hash = %s, must_change_password = true WHERE id = %s RETURNING id, name', (hashed, uid))
    result = cur.fetchone()
    if result:
        print(f'Reset password for: ID={{result[0]}}, Name={{result[1]}}')
    else:
        print(f'User ID {{uid}} not found')

conn.commit()
cur.close()
conn.close()
print('All passwords reset to 123456 with must_change_password=true')
"
"""

stdin, stdout, stderr = ssh.exec_command(reset_cmd)
out = stdout.read().decode()
err = stderr.read().decode()
print(f'Output: {out}')
if err and 'DeprecationWarning' not in err and 'UserWarning' not in err:
    print(f'Error: {err}')

ssh.close()
print('Done.')
