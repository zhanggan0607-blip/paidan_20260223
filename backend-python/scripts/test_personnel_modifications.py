import requests
import time

print("=" * 80)
print("测试人员管理API修改结果")
print("=" * 80)

base_url = "http://localhost:8080/api/v1"

print("\n1. 测试获取人员列表...")
try:
    start_time = time.time()
    response = requests.get(f"{base_url}/personnel/all/list", timeout=10)
    end_time = time.time()
    response_time = (end_time - start_time) * 1000
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ 获取人员列表: {response_time:.2f}ms (状态码: {response.status_code})")
        print(f"      数据量: {len(data['data'])}")
        
        if len(data['data']) > 0:
            print(f"      示例数据:")
            person = data['data'][0]
            print(f"         ID: {person.get('id')}")
            print(f"         姓名: {person.get('name')}")
            print(f"         性别: {person.get('gender')}")
            print(f"         联系电话: {person.get('phone')}")
            print(f"         部门: {person.get('department')}")
            print(f"         角色: {person.get('role')}")
            print(f"         地址: {person.get('address')}")
            print(f"         备注: {person.get('remarks')}")
            
            # 检查是否还有旧字段
            if 'employee_id' in person:
                print(f"      ❌ 发现旧字段: employee_id")
            if 'age' in person:
                print(f"      ❌ 发现旧字段: age")
            if 'email' in person:
                print(f"      ❌ 发现旧字段: email")
            if 'position' in person:
                print(f"      ❌ 发现旧字段: position")
            if 'status' in person:
                print(f"      ❌ 发现旧字段: status")
            else:
                print(f"      ✅ 未发现旧字段")
    else:
        print(f"   ❌ 获取人员列表: {response.status_code}")
except Exception as e:
    print(f"   ❌ 获取人员列表错误: {str(e)}")

print("\n2. 测试创建人员...")
try:
    create_data = {
        "name": "测试人员",
        "gender": "男",
        "phone": "13800138000",
        "department": "技术部",
        "role": "员工",
        "address": "测试地址",
        "remarks": "测试备注"
    }
    
    response = requests.post(f"{base_url}/personnel", json=create_data, timeout=10)
    
    if response.status_code in [200, 201]:
        data = response.json()
        print(f"   ✅ 创建人员成功: {response.status_code}")
        print(f"      新人员ID: {data['data']['id']}")
        
        # 测试删除
        new_id = data['data']['id']
        delete_response = requests.delete(f"{base_url}/personnel/{new_id}", timeout=10)
        if delete_response.status_code == 200:
            print(f"   ✅ 删除测试人员成功")
        else:
            print(f"   ❌ 删除测试人员失败: {delete_response.status_code}")
    else:
        print(f"   ❌ 创建人员失败: {response.status_code}")
        print(f"      错误信息: {response.text}")
except Exception as e:
    print(f"   ❌ 创建人员错误: {str(e)}")

print("\n3. 测试分页查询...")
try:
    start_time = time.time()
    response = requests.get(f"{base_url}/personnel?page=0&size=10", timeout=10)
    end_time = time.time()
    response_time = (end_time - start_time) * 1000
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ 分页查询: {response_time:.2f}ms (状态码: {response.status_code})")
        print(f"      总记录数: {data['data']['totalElements']}")
        print(f"      总页数: {data['data']['totalPages']}")
        print(f"      当前页记录数: {len(data['data']['content'])}")
    else:
        print(f"   ❌ 分页查询失败: {response.status_code}")
except Exception as e:
    print(f"   ❌ 分页查询错误: {str(e)}")

print("\n" + "=" * 80)
print("测试完成！")
print("=" * 80)
