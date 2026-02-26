import requests
from urllib.parse import quote

headers = {
    'X-User-Name': 'admin',
    'X-User-Role': quote('管理员')
}
r = requests.get('http://localhost:8080/api/v1/work-plan/statistics', headers=headers)
print(r.json())
