import requests
import json
from datetime import datetime, timedelta

print("=" * 80)
print("测试数据插入功能")
print("=" * 80)

base_url = "http://localhost:8080/api/v1/maintenance-plan"

print("\n1. 测试GET请求 - 查询当前数据")
print("-" * 80)

try:
    r = requests.get(base_url, params={'page': 0, 'size': 10}, timeout=10)
    print(f"状态码: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        print(f"✅ 查询成功")
        print(f"总记录数: {data['data']['totalElements']}")
        print(f"当前页记录数: {len(data['data']['content'])}")
    else:
        print(f"❌ 查询失败: {r.text}")
except Exception as e:
    print(f"❌ 请求异常: {e}")

print("\n2. 测试POST请求 - 插入新数据")
print("-" * 80)

test_data = {
    "plan_id": f"TEST{datetime.now().strftime('%Y%m%d%H%M%S')}",
    "plan_name": "自动化测试维保计划",
    "project_id": "AUTO001",
    "plan_type": "定期维保",
    "equipment_id": "AUTO-EQ001",
    "equipment_name": "自动化测试设备",
    "equipment_model": "AUTO-MODEL-001",
    "equipment_location": "自动化测试地点",
    "plan_start_date": "2024-01-01T00:00:00",
    "plan_end_date": "2024-12-31T00:00:00",
    "execution_date": "2024-06-15T00:00:00",
    "next_maintenance_date": "2024-07-15T00:00:00",
    "responsible_person": "自动化测试员",
    "responsible_department": "测试部",
    "contact_info": "13900139000",
    "maintenance_content": "自动化测试维保内容",
    "maintenance_requirements": "自动化测试要求",
    "maintenance_standard": "自动化测试标准",
    "plan_status": "待执行",
    "execution_status": "未开始",
    "completion_rate": 0,
    "remarks": "自动化测试数据"
}

try:
    r = requests.post(base_url, json=test_data, timeout=10)
    print(f"状态码: {r.status_code}")
    
    if r.status_code == 201:
        response = r.json()
        print(f"✅ 插入成功")
        print(f"返回数据: {json.dumps(response, indent=2, ensure_ascii=False)}")
        
        inserted_id = response['data']['id']
        inserted_plan_id = response['data']['plan_id']
        
        print("\n3. 验证数据是否成功插入")
        print("-" * 80)
        
        r2 = requests.get(base_url, params={'page': 0, 'size': 10}, timeout=10)
        if r2.status_code == 200:
            data2 = r2.json()
            print(f"✅ 查询成功")
            print(f"插入后总记录数: {data2['data']['totalElements']}")
            
            if data2['data']['totalElements'] > 0:
                latest_record = data2['data']['content'][0]
                print(f"\n最新记录:")
                print(f"  ID: {latest_record['id']}")
                print(f"  计划ID: {latest_record['plan_id']}")
                print(f"  计划名称: {latest_record['plan_name']}")
                print(f"  创建时间: {latest_record['created_at']}")
                
                print("\n4. 测试根据ID查询")
                print("-" * 80)
                
                r3 = requests.get(f"{base_url}/{inserted_id}", timeout=10)
                if r3.status_code == 200:
                    print(f"✅ 根据ID查询成功")
                    print(f"查询结果: {json.dumps(r3.json(), indent=2, ensure_ascii=False)}")
                else:
                    print(f"❌ 根据ID查询失败: {r3.text}")
        else:
            print(f"❌ 查询失败: {r2.text}")
    else:
        print(f"❌ 插入失败: {r.text}")
        
except Exception as e:
    print(f"❌ 请求异常: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
