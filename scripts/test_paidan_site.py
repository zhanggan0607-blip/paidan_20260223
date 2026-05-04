import os
import urllib.request
import urllib.error
import ssl
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE = 'https://www.paidan.sstcp.top'

def api_post_json(path, data, token=None):
    headers = {'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(f'{BASE}{path}', data=body, headers=headers)
    try:
        r = urllib.request.urlopen(req, context=ctx, timeout=15)
        return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        try:
            return e.code, json.loads(body_text)
        except:
            return e.code, body_text

def api_get(path, token=None):
    headers = {'User-Agent': 'Mozilla/5.0'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(f'{BASE}{path}', headers=headers)
    try:
        r = urllib.request.urlopen(req, context=ctx, timeout=15)
        return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        try:
            return e.code, json.loads(body_text)
        except:
            return e.code, body_text

results = []

def test(name, status_code, expected=200):
    ok = 'PASS' if status_code == expected else 'FAIL'
    results.append((name, status_code, expected, ok))
    print(f'  [{ok}] {name}: {status_code}')

print('=== Login Test ===')
status, resp = api_post_json('/api/v1/auth/login-json', {
    'username': os.environ.get('TEST_USERNAME', ''),
    'password': os.environ.get('TEST_PASSWORD', ''),
    'device_type': 'pc'
})
test('PC Login', status)
token = resp.get('data', {}).get('access_token') if status == 200 and isinstance(resp, dict) else None

if not token:
    print('[FAIL] Login failed')
    exit(1)

print(f'\n=== API Endpoint Tests ===')

endpoints = [
    ('Health Check', '/api/v1/health', False),
    ('Project Info', '/api/v1/project-info?page=1&size=5', True),
    ('Work Plan Stats', '/api/v1/work-plan/statistics', True),
    ('Top Projects', '/api/v1/statistics/top-projects?year=2026&limit=5', True),
    ('Work Order Distribution', '/api/v1/statistics/work-order-distribution?year=2026', True),
    ('Personnel', '/api/v1/personnel?page=1&size=5', True),
    ('Maintenance Plans', '/api/v1/maintenance-plan?page=1&size=5', True),
    ('Periodic Inspections', '/api/v1/periodic-inspection?page=1&size=5', True),
    ('Temporary Repairs', '/api/v1/temporary-repair?page=1&size=5', True),
    ('Spot Work', '/api/v1/spot-work?page=1&size=5', True),
    ('Spare Parts Stock', '/api/v1/spare-parts-stock/stock?page=1&size=5', True),
    ('Repair Tools Stock', '/api/v1/repair-tools/stock?page=1&size=5', True),
    ('Customers', '/api/v1/customer?page=1&size=5', True),
    ('Dictionary', '/api/v1/dictionary?page=1&size=5', True),
    ('Maintenance Logs', '/api/v1/maintenance-log?page=1&size=5', True),
    ('Weekly Reports', '/api/v1/weekly-report?page=1&size=5', True),
    ('Online Users', '/api/v1/online/users', True),
    ('Expiring Soon', '/api/v1/expiring-soon', True),
]

for name, path, need_auth in endpoints:
    t = token if need_auth else None
    status_code, _ = api_get(path, t)
    test(name, status_code)

print(f'\n=== Page Tests ===')
for path, name in [('/', 'PC Homepage'), ('/h5/', 'H5 Homepage')]:
    try:
        req = urllib.request.Request(f'{BASE}{path}', headers={'User-Agent': 'Mozilla/5.0'})
        r = urllib.request.urlopen(req, context=ctx, timeout=15)
        test(name, r.status)
    except Exception as e:
        test(name, 0)

print(f'\n=== Summary ===')
passed = sum(1 for _, s, e, _ in results if s == e)
failed = sum(1 for _, s, e, _ in results if s != e)
print(f'Passed: {passed}/{len(results)}')
if failed > 0:
    print(f'Failed:')
    for name, status_code, expected, ok in results:
        if status_code != expected:
            print(f'  [FAIL] {name}: got {status_code}, expected {expected}')
