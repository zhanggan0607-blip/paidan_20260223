"""测试临时维修API返回的数据"""
import requests

response = requests.get('http://localhost:8000/api/v1/temporary-repair?page=0&size=10')
data = response.json()

if data.get('code') == 200:
    items = data.get('data', {}).get('content', [])
    print(f"共 {len(items)} 条记录")
    for item in items[:10]:
        print(f"ID: {item.get('id')}, repair_id: {item.get('repair_id')}, status: {item.get('status')}")
else:
    print('API Error:', data)
