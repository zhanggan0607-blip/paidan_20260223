import requests
import json
from datetime import datetime, timedelta

print("Testing maintenance plan creation...")
test_plan_id = f"TEST{datetime.now().strftime('%Y%m%d%H%M%S')}"

create_data = {
    "plan_id": test_plan_id,
    "plan_name": "测试维保计划",
    "project_id": "TEST001",
    "plan_type": "定期维保",
    "equipment_id": "EQ001",
    "equipment_name": "测试设备",
    "equipment_model": "MODEL-001",
    "equipment_location": "测试地点",
    "plan_start_date": "2024-01-01T00:00:00",
    "plan_end_date": "2024-12-31T00:00:00",
    "execution_date": "2024-06-15T00:00:00",
    "next_maintenance_date": "2024-07-15T00:00:00",
    "responsible_person": "张三",
    "responsible_department": "维保部",
    "contact_info": "13800138000",
    "maintenance_content": "定期检查设备运行状态，更换易损件",
    "maintenance_requirements": "需要停机操作",
    "maintenance_standard": "按照设备维护手册执行",
    "plan_status": "待执行",
    "execution_status": "未开始",
    "completion_rate": 0,
    "remarks": "测试数据"
}

try:
    r = requests.post('http://localhost:8080/api/v1/maintenance-plan', json=create_data, timeout=10)
    print(f"Status: {r.status_code}")
    
    if r.status_code == 201:
        response = r.json()
        print("Response:", json.dumps(response, indent=2, ensure_ascii=False))
        print("\n✅ Maintenance plan created successfully!")
        print(f"Plan ID: {response['data']['plan_id']}")
        print(f"ID: {response['data']['id']}")
    else:
        print(f"Error: {r.status_code}")
        print("Response:", r.text)
        
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
