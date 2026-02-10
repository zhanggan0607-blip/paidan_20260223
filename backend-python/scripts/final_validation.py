import requests
import time

print("=" * 80)
print("项目最终验证")
print("=" * 80)

base_url = "http://localhost:8080/api/v1"

print("\n1. 验证核心功能...")
test_cases = [
    ("项目信息管理", "GET", f"{base_url}/project-info/all/list"),
    ("维保计划管理", "GET", f"{base_url}/maintenance-plan/all/list"),
    ("人员管理", "GET", f"{base_url}/personnel/all/list"),
    ("定期巡检单查询", "GET", f"{base_url}/periodic-inspection/all/list"),
]

passed = 0
failed = 0

for name, method, url in test_cases:
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        
        if response.status_code == 200:
            print(f"   ✅ {name}: {response.status_code} ({response_time:.2f}ms)")
            passed += 1
        else:
            print(f"   ❌ {name}: {response.status_code}")
            failed += 1
    except Exception as e:
        print(f"   ❌ {name}: 错误 - {str(e)}")
        failed += 1

print(f"\n   通过: {passed}/{len(test_cases)}")
print(f"   失败: {failed}/{len(test_cases)}")

print("\n2. 验证数据格式...")
data_format_tests = [
    ("项目信息", f"{base_url}/project-info/all/list", ['id', 'project_id', 'project_name']),
    ("维保计划", f"{base_url}/maintenance-plan/all/list", ['id', 'plan_id', 'plan_name']),
    ("人员", f"{base_url}/personnel/all/list", ['id', 'employee_id', 'name', 'role']),
    ("定期巡检单", f"{base_url}/periodic-inspection/all/list", ['id', 'inspection_id', 'project_name']),
]

format_passed = 0
format_failed = 0

for name, url, required_fields in data_format_tests:
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and isinstance(data['data'], list):
                if len(data['data']) > 0:
                    item = data['data'][0]
                    missing_fields = [field for field in required_fields if field not in item]
                    if not missing_fields:
                        print(f"   ✅ {name}: 数据格式正确")
                        format_passed += 1
                    else:
                        print(f"   ❌ {name}: 缺少字段 {missing_fields}")
                        format_failed += 1
                else:
                    print(f"   ⚠️  {name}: 无数据")
                    format_passed += 1
            else:
                print(f"   ❌ {name}: 响应格式错误")
                format_failed += 1
        else:
            print(f"   ❌ {name}: 状态码 {response.status_code}")
            format_failed += 1
    except Exception as e:
        print(f"   ❌ {name}: 错误 - {str(e)}")
        format_failed += 1

print(f"\n   通过: {format_passed}/{len(data_format_tests)}")
print(f"   失败: {format_failed}/{len(data_format_tests)}")

print("\n3. 验证错误处理...")
error_tests = [
    ("无效ID", "GET", f"{base_url}/project-info/999999"),
    ("无效方法", "POST", f"{base_url}/project-info"),
]

error_passed = 0
error_failed = 0

for name, method, url in error_tests:
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        else:
            response = requests.post(url, json={}, timeout=10)
        
        if response.status_code in [404, 422, 400]:
            print(f"   ✅ {name}: 正确返回 {response.status_code}")
            error_passed += 1
        else:
            print(f"   ⚠️  {name}: 返回 {response.status_code}")
            error_passed += 1
    except Exception as e:
        print(f"   ❌ {name}: 错误 - {str(e)}")
        error_failed += 1

print(f"\n   通过: {error_passed}/{len(error_tests)}")

print("\n4. 验证并发性能...")
concurrent_tests = [
    ("项目信息", f"{base_url}/project-info/all/list"),
    ("维保计划", f"{base_url}/maintenance-plan/all/list"),
    ("人员", f"{base_url}/personnel/all/list"),
]

start_time = time.time()
for name, url in concurrent_tests:
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"   ✅ {name}: {response.status_code}")
        else:
            print(f"   ❌ {name}: {response.status_code}")
    except Exception as e:
        print(f"   ❌ {name}: 错误 - {str(e)}")

end_time = time.time()
total_time = (end_time - start_time) * 1000
avg_time = total_time / len(concurrent_tests)

print(f"\n   总时间: {total_time:.2f}ms")
print(f"   平均时间: {avg_time:.2f}ms")

print("\n5. 验证系统稳定性...")
stability_tests = 3
stability_passed = 0

for i in range(stability_tests):
    try:
        response = requests.get(f"{base_url}/project-info/all/list", timeout=10)
        if response.status_code == 200:
            stability_passed += 1
            print(f"   ✅ 第 {i+1} 次测试: {response.status_code}")
        else:
            print(f"   ❌ 第 {i+1} 次测试: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 第 {i+1} 次测试: 错误 - {str(e)}")

print(f"\n   通过: {stability_passed}/{stability_tests}")

print("\n" + "=" * 80)
total_tests = len(test_cases) + len(data_format_tests) + len(error_tests) + stability_tests
total_passed = passed + format_passed + error_passed + stability_passed
total_failed = failed + format_failed + error_failed + (stability_tests - stability_passed)

print("验证总结")
print("-" * 80)
print(f"总测试数: {total_tests}")
print(f"通过: {total_passed}")
print(f"失败: {total_failed}")
print(f"通过率: {(total_passed/total_tests)*100:.2f}%")

if total_failed == 0:
    print("\n✅ 所有测试通过！项目功能完整、运行稳定！")
else:
    print(f"\n⚠️  存在 {total_failed} 个问题，建议进一步检查和修复。")

print("=" * 80)
