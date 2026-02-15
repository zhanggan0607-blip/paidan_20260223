import requests

r = requests.get('http://localhost:8080/api/v1/periodic-inspection', params={'page': 0, 'size': 5, 'status': '待执行'})
data = r.json()
items = data['data']['content']

for item in items[:3]:
    update_data = {
        'inspection_id': item['inspection_id'],
        'project_id': item['project_id'],
        'project_name': item['project_name'],
        'plan_start_date': item['plan_start_date'],
        'plan_end_date': item['plan_end_date'],
        'client_name': item['client_name'],
        'maintenance_personnel': item['maintenance_personnel'],
        'status': '待确认',
        'filled_count': item.get('filled_count', 0),
        'remarks': item.get('remarks', '')
    }
    r2 = requests.put(f"http://localhost:8080/api/v1/periodic-inspection/{item['id']}", json=update_data)
    print(f"更新工单 {item['inspection_id']} 状态为待确认: {r2.status_code}")

print('完成!')
