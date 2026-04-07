"""测试前端实际获取的数据"""
import requests

# 模拟前端请求
response = requests.get(
    'http://localhost:8000/api/v1/temporary-repair?page=0&size=1000'
)
data = response.json()

if data.get('code') == 200:
    items = data.get('data', {}).get('content', [])
    
    # 模拟前端过滤逻辑
    valid_statuses = ['执行中', '待确认', '已退回']
    filtered_items = [item for item in items if item.get('status') in valid_statuses]
    
    print(f"过滤后共 {len(filtered_items)} 条记录")
    print()
    print("=== 过滤后的数据 ===")
    for item in filtered_items:
        print(f"ID: {item.get('id')}, repair_id: {item.get('repair_id')}, status: {item.get('status')}")
else:
    print('API Error:', data)
