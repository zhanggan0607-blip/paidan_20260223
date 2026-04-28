import paramiko
import json
import sys
import urllib.request
import urllib.error

SERVER_IP = '8.153.95.31'
SERVER_PASSWORD = os.environ.get('SERVER_PASSWORD', '')
API_BASE = f'https://{SERVER_IP}/api/v1'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER_IP, username='root', password=SERVER_PASSWORD, timeout=15)

stdin, stdout, stderr = ssh.exec_command("""docker exec sstcp-backend python -c "
import psycopg2
import json

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

def test_login(username, password, device_type='pc'):
    url = f'{API_BASE}/auth/login-json'
    data = json.dumps({
        'username': username,
        'password': password,
        'device_type': device_type
    }).encode('utf-8')

    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            result = json.loads(resp.read().decode())
            return True, result
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            result = json.loads(body)
            return False, result
        except:
            return False, {'status': e.code, 'detail': body}
    except Exception as e:
        return False, {'error': str(e)}

results = []

for user in users:
    name = user['name']
    role = user['role']
    department = user.get('department', '') or ''
    phone = user.get('phone', '') or ''
    has_password = user['has_password']
    must_change = user['must_change_password']

    print(f'\n--- Testing user: {name} (ID:{user["id"]}, Role:{role}, Dept:{department}) ---')
    print(f'    Has password hash: {has_password}, Must change password: {must_change}, Phone: {phone}')

    passwords_to_try = ['123456']
    if phone and len(phone) >= 6:
        passwords_to_try.append(phone[-6:])

    login_success = False
    login_password = None
    login_result = None

    for pwd in passwords_to_try:
        success, result = test_login(name, pwd, 'pc')
        if success:
            login_success = True
            login_password = pwd
            login_result = result
            break
        else:
            login_result = result

    pc_ok = login_success
    pc_password = login_password

    if login_success:
        h5_success, h5_result = test_login(name, login_password, 'h5')
        h5_ok = h5_success
    else:
        h5_ok = False

    user_result = {
        'id': user['id'],
        'name': name,
        'role': role,
        'department': department,
        'has_password': has_password,
        'must_change_password': must_change,
        'pc_login': pc_ok,
        'h5_login': h5_ok,
        'password_used': login_password,
    }

    if not login_success and login_result:
        detail = ''
        if isinstance(login_result, dict):
            detail = login_result.get('detail', login_result.get('message', str(login_result)))
        user_result['error'] = detail

    results.append(user_result)

    status_pc = '✅' if pc_ok else '❌'
    status_h5 = '✅' if h5_ok else '❌'
    pwd_info = f'(pwd: {login_password})' if login_password else '(no valid password found)'
    print(f'    PC Login: {status_pc}  H5 Login: {status_h5}  {pwd_info}')
    if not login_success:
        print(f'    Error: {user_result.get("error", "Unknown")}')

print('\n\n' + '=' * 80)
print('SUMMARY REPORT')
print('=' * 80)

success_users = [r for r in results if r['pc_login'] and r['h5_login']]
pc_only_fail = [r for r in results if not r['pc_login'] and r['h5_login']]
h5_only_fail = [r for r in results if r['pc_login'] and not r['h5_login']]
both_fail = [r for r in results if not r['pc_login'] and not r['h5_login']]

print(f'\nTotal users: {len(results)}')
print(f'Both PC+H5 login OK: {len(success_users)}')
print(f'PC only fail: {len(pc_only_fail)}')
print(f'H5 only fail: {len(h5_only_fail)}')
print(f'Both fail: {len(both_fail)}')

if both_fail:
    print('\n--- Users that CANNOT login (both PC and H5) ---')
    for r in both_fail:
        print(f'  ❌ {r["name"]} (ID:{r["id"]}, Role:{r["role"]}, Dept:{r["department"]})')
        print(f'     Has password: {r["has_password"]}, Must change: {r["must_change_password"]}')
        print(f'     Error: {r.get("error", "Unknown")}')

if h5_only_fail:
    print('\n--- Users that can login PC but NOT H5 ---')
    for r in h5_only_fail:
        print(f'  ⚠️ {r["name"]} (ID:{r["id"]}, Role:{r["role"]})')

if success_users:
    print('\n--- Users that CAN login both PC and H5 ---')
    for r in success_users:
        must_change_flag = ' [MUST CHANGE PWD]' if r['must_change_password'] else ''
        print(f'  ✅ {r["name"]} (ID:{r["id"]}, Role:{r["role"]}, Pwd: {r["password_used"]}){must_change_flag}')

ssh.close()
print('\nDone.')
