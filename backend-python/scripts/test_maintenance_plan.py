import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8080/api/v1/maintenance-plan"

def test_maintenance_plan_api():
    print("=" * 80)
    print("维保计划管理系统功能测试")
    print("=" * 80)
    
    test_plan_id = f"TEST{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    print("\n1️⃣ 测试创建维保计划...")
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
        response = requests.post(BASE_URL, json=create_data)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
        
        if response.status_code == 201:
            print("   ✅ 创建成功")
            created_plan = response.json()['data']
            plan_id = created_plan['id']
        else:
            print(f"   ❌ 创建失败: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ 创建异常: {str(e)}")
        return
    
    print("\n2️⃣ 测试查询维保计划列表...")
    try:
        response = requests.get(BASE_URL, params={
            "page": 0,
            "size": 10
        })
        print(f"   状态码: {response.status_code}")
        result = response.json()
        print(f"   总记录数: {result['data']['totalElements']}")
        print(f"   当前页记录数: {len(result['data']['content'])}")
        print("   ✅ 查询成功")
    except Exception as e:
        print(f"   ❌ 查询异常: {str(e)}")
    
    print("\n3️⃣ 测试根据ID查询维保计划...")
    try:
        response = requests.get(f"{BASE_URL}/{plan_id}")
        print(f"   状态码: {response.status_code}")
        print(f"   计划名称: {response.json()['data']['plan_name']}")
        print("   ✅ 查询成功")
    except Exception as e:
        print(f"   ❌ 查询异常: {str(e)}")
    
    print("\n4️⃣ 测试更新维保计划...")
    update_data = {
        "plan_id": test_plan_id,
        "plan_name": "测试维保计划（已更新）",
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
        "maintenance_content": "定期检查设备运行状态，更换易损件（已更新）",
        "maintenance_requirements": "需要停机操作",
        "maintenance_standard": "按照设备维护手册执行",
        "plan_status": "执行中",
        "execution_status": "进行中",
        "completion_rate": 50,
        "remarks": "测试数据（已更新）"
    }
    
    try:
        response = requests.put(f"{BASE_URL}/{plan_id}", json=update_data)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
        
        if response.status_code == 200:
            print("   ✅ 更新成功")
        else:
            print(f"   ❌ 更新失败: {response.text}")
    except Exception as e:
        print(f"   ❌ 更新异常: {str(e)}")
    
    print("\n5️⃣ 测试更新执行状态...")
    try:
        response = requests.patch(f"{BASE_URL}/{plan_id}/status", params={"status": "已完成"})
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
        
        if response.status_code == 200:
            print("   ✅ 状态更新成功")
        else:
            print(f"   ❌ 状态更新失败: {response.text}")
    except Exception as e:
        print(f"   ❌ 状态更新异常: {str(e)}")
    
    print("\n6️⃣ 测试更新完成率...")
    try:
        response = requests.patch(f"{BASE_URL}/{plan_id}/completion-rate", params={"rate": 100})
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
        
        if response.status_code == 200:
            print("   ✅ 完成率更新成功")
        else:
            print(f"   ❌ 完成率更新失败: {response.text}")
    except Exception as e:
        print(f"   ❌ 完成率更新异常: {str(e)}")
    
    print("\n7️⃣ 测试条件查询...")
    try:
        response = requests.get(BASE_URL, params={
            "page": 0,
            "size": 10,
            "plan_status": "已完成",
            "execution_status": "已完成"
        })
        print(f"   状态码: {response.status_code}")
        result = response.json()
        print(f"   查询结果数: {len(result['data']['content'])}")
        print("   ✅ 条件查询成功")
    except Exception as e:
        print(f"   ❌ 条件查询异常: {str(e)}")
    
    print("\n8️⃣ 测试获取所有维保计划...")
    try:
        response = requests.get(f"{BASE_URL}/all/list")
        print(f"   状态码: {response.status_code}")
        result = response.json()
        print(f"   总记录数: {len(result['data'])}")
        print("   ✅ 获取成功")
    except Exception as e:
        print(f"   ❌ 获取异常: {str(e)}")
    
    print("\n9️⃣ 测试获取即将到期的维保计划...")
    try:
        response = requests.get(f"{BASE_URL}/upcoming/list", params={"days": 30})
        print(f"   状态码: {response.status_code}")
        result = response.json()
        print(f"   即将到期记录数: {len(result['data'])}")
        print("   ✅ 获取成功")
    except Exception as e:
        print(f"   ❌ 获取异常: {str(e)}")
    
    print("\n🔟 测试根据项目编号查询...")
    try:
        response = requests.get(f"{BASE_URL}/project/TEST001")
        print(f"   状态码: {response.status_code}")
        result = response.json()
        print(f"   项目记录数: {len(result['data'])}")
        print("   ✅ 查询成功")
    except Exception as e:
        print(f"   ❌ 查询异常: {str(e)}")
    
    print("\n1️⃣1️⃣ 测试根据日期范围查询...")
    try:
        response = requests.get(f"{BASE_URL}/date-range/list", params={
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        })
        print(f"   状态码: {response.status_code}")
        result = response.json()
        print(f"   日期范围内记录数: {len(result['data'])}")
        print("   ✅ 查询成功")
    except Exception as e:
        print(f"   ❌ 查询异常: {str(e)}")
    
    print("\n1️⃣2️⃣ 测试删除维保计划...")
    try:
        response = requests.delete(f"{BASE_URL}/{plan_id}")
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
        
        if response.status_code == 200:
            print("   ✅ 删除成功")
        else:
            print(f"   ❌ 删除失败: {response.text}")
    except Exception as e:
        print(f"   ❌ 删除异常: {str(e)}")
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)


if __name__ == "__main__":
    test_maintenance_plan_api()
