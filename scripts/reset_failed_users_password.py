import paramiko
import os
import json
import secrets
import string
import sys
import urllib.request
import urllib.error

SERVER_IP = os.environ.get('SERVER_IP', '')
SERVER_PASSWORD = os.environ.get('SERVER_PASSWORD', '')
API_BASE = f'https://{SERVER_IP}/api/v1'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
known_hosts = os.path.expanduser('~/.ssh/known_hosts')
if os.path.exists(known_hosts):
    ssh.load_host_keys(known_hosts)
ssh.connect(SERVER_IP, username='root', password=SERVER_PASSWORD, timeout=15)

stdin, stdout, stderr = ssh.exec_command("""docker exec sstcp-backend python -c "
import psycopg2
import json
import os

conn = psycopg2.connect(os.environ.get('DATABASE_URL', ''))
cur = conn.cursor()
cur.execute('SELECT id, name, role, department, phone, password_hash, must_change_password FROM personnel ORDER BY id')
rows = cur.fetchall()
users = []
for row in rows:
    users.append({
        'id': row[0],
        'name': row[1],
        'role': row[2],
        'department': row[3],
        'phone': row[4],
        'has_password': row[5] is not None and row[5] != '',
        'must_change_password': row[6]
    })
print(json.dumps(users, ensure_ascii=False))
cur.close()
conn.close()
"
""")

out = stdout.read().decode()
err = stderr.read().decode()

if err and 'DeprecationWarning' not in err and 'UserWarning' not in err:
    print(f'DB query error: {err}')

try:
    users = json.loads(out.strip().split('\n')[-1] if '\n' in out.strip() else out.strip())
except json.JSONDecodeError:
    print(f'Failed to parse users: {out}')
    ssh.close()
    sys.exit(1)

print(f'Found {len(users)} users in database\n')
print('=' * 80)

def generate_temp_password(length=12):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def reset_password(ssh_conn, user_id, new_password):
    hash_cmd = """docker exec sstcp-backend python -c "
import sys
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
hashed = pwd_context.hash(sys.argv[1])
print(hashed)
" %s
""" % new_password.replace("'", "'\\''")
    stdin_h, stdout_h, stderr_h = ssh_conn.exec_command(hash_cmd)
    hashed = stdout_h.read().decode().strip()
    if not hashed:
        return False

    update_cmd = """docker exec sstcp-backend python -c "
import psycopg2
import os
import sys
conn = psycopg2.connect(os.environ.get('DATABASE_URL', ''))
cur = conn.cursor()
cur.execute('UPDATE personnel SET password_hash = %s, must_change_password = true WHERE id = %s', (sys.argv[1], int(sys.argv[2])))
conn.commit()
cur.close()
conn.close()
print('OK')
" '%s' '%s'
""" % (hashed.replace("'", "'\\''"), user_id)
    stdin_u, stdout_u, stderr_u = ssh_conn.exec_command(update_cmd)
    result = stdout_u.read().decode().strip()
    return result == 'OK'

failed_users = []
for user in users:
    name = user['name']
    role = user['role']
    has_password = user['has_password']
    must_change = user['must_change_password']

    if not has_password:
        temp_pwd = generate_temp_password()
        success = reset_password(ssh, user['id'], temp_pwd)
        if success:
            print(f'✅ {name} (ID:{user["id"]}, Role:{role}) - 密码已重置为临时密码, 首次登录需修改')
            failed_users.append({'name': name, 'id': user['id'], 'temp_password': temp_pwd, 'reset': True})
        else:
            print(f'❌ {name} (ID:{user["id"]}, Role:{role}) - 密码重置失败')
            failed_users.append({'name': name, 'id': user['id'], 'reset': False})
    else:
        print(f'⏭️ {name} (ID:{user["id"]}, Role:{role}) - 已有密码, 跳过')

print('\n' + '=' * 80)
print('SUMMARY')
print('=' * 80)
reset_ok = [u for u in failed_users if u.get('reset')]
reset_fail = [u for u in failed_users if not u.get('reset')]
print(f'\n重置成功: {len(reset_ok)}')
for u in reset_ok:
    print(f'  {u["name"]} (ID:{u["id"]}) - 临时密码: {u["temp_password"]}')
print(f'\n重置失败: {len(reset_fail)}')
for u in reset_fail:
    print(f'  {u["name"]} (ID:{u["id"]})')

ssh.close()
print('\nDone.')
