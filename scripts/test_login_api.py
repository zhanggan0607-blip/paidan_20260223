import urllib.request
import json

data = json.dumps({'username': 'admin', 'password': '123456', 'device_type': 'pc'}).encode()
req = urllib.request.Request('http://localhost:8000/api/v1/auth/login', data=data, headers={'Content-Type': 'application/json'})
try:
    r = urllib.request.urlopen(req, timeout=10)
    print(f'Status: {r.status}')
    print(f'Response: {r.read().decode()[:500]}')
except urllib.error.HTTPError as e:
    print(f'Error: {e.code}')
    print(f'Body: {e.read().decode()[:500]}')
