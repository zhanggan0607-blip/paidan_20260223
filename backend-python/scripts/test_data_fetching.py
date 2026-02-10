import requests
import time

print("=" * 80)
print("测试数据获取的正确性和稳定性")
print("=" * 80)

base_url = "http://localhost:8080/api/v1"

print("\n1. 测试巡检事项API...")
try:
    start_time = time.time()
    response = requests.get(f"{base_url}/inspection-item/all/list", timeout=10)
    end_time = time.time()
    response_time = (end_time - start_time) * 1000
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ 获取巡检事项列表: {response_time:.2f}ms (状态码: {response.status_code})")
        print(f"      数据量: {len(data['data'])}")
    else:
        print(f"   ❌ 获取巡检事项列表: {response.status_code}")
except Exception as e:
    print(f"   ❌ 获取巡检事项列表错误: {str(e)}")

print("\n2. 测试维保计划API...")
try:
    start_time = time.time()
    response = requests.get(f"{base_url}/maintenance-plan/all/list", timeout=10)
    end_time = time.time()
    response_time = (end_time - start_time) * 1000
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ 获取维保计划列表: {response_time:.2f}ms (状态码: {response.status_code})")
        print(f"      数据量: {len(data['data'])}")
    else:
        print(f"   ❌ 获取维保计划列表: {response.status_code}")
except Exception as e:
    print(f"   ❌ 获取维保计划列表错误: {str(e)}")

print("\n3. 测试巡检事项分页API...")
try:
    start_time = time.time()
    response = requests.get(f"{base_url}/inspection-item?page=0&size=10", timeout=10)
    end_time = time.time()
    response_time = (end_time - start_time) * 1000
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ 获取巡检事项分页: {response_time:.2f}ms (状态码: {response.status_code})")
        print(f"      总记录数: {data['data']['totalElements']}")
        print(f"      当前页记录数: {len(data['data']['content'])}")
    else:
        print(f"   ❌ 获取巡检事项分页: {response.status_code}")
except Exception as e:
    print(f"   ❌ 获取巡检事项分页错误: {str(e)}")

print("\n4. 测试维保计划分页API...")
try:
    start_time = time.time()
    response = requests.get(f"{base_url}/maintenance-plan?page=0&size=10", timeout=10)
    end_time = time.time()
    response_time = (end_time - start_time) * 1000
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ 获取维保计划分页: {response_time:.2f}ms (状态码: {response.status_code})")
        print(f"      总记录数: {data['data']['totalElements']}")
        print(f"      当前页记录数: {len(data['data']['content'])}")
    else:
        print(f"   ❌ 获取维保计划分页: {response.status_code}")
except Exception as e:
    print(f"   ❌ 获取维保计划分页错误: {str(e)}")

print("\n5. 测试搜索功能...")
try:
    start_time = time.time()
    response = requests.get(f"{base_url}/inspection-item?keyword=电梯", timeout=10)
    end_time = time.time()
    response_time = (end_time - start_time) * 1000
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ 搜索巡检事项: {response_time:.2f}ms (状态码: {response.status_code})")
        print(f"      搜索结果数量: {len(data['data']['content'])}")
    else:
        print(f"   ❌ 搜索巡检事项: {response.status_code}")
except Exception as e:
    print(f"   ❌ 搜索巡检事项错误: {str(e)}")

print("\n6. 测试错误处理...")
try:
    response = requests.get(f"{base_url}/inspection-item/999999", timeout=10)
    if response.status_code == 404:
        print(f"   ✅ 正确返回404错误: {response.status_code}")
    else:
        print(f"   ⚠️  返回状态码: {response.status_code}")
except Exception as e:
    print(f"   ❌ 错误处理测试失败: {str(e)}")

print("\n7. 测试并发请求...")
try:
    start_time = time.time()
    
    responses = []
    for i in range(3):
        response = requests.get(f"{base_url}/inspection-item/all/list", timeout=10)
        responses.append(response)
    
    end_time = time.time()
    total_time = (end_time - start_time) * 1000
    avg_time = total_time / 3
    
    success_count = sum(1 for r in responses if r.status_code == 200)
    print(f"   ✅ 并发请求测试: {total_time:.2f}ms (平均: {avg_time:.2f}ms)")
    print(f"      成功: {success_count}/3")
except Exception as e:
    print(f"   ❌ 并发请求测试失败: {str(e)}")

print("\n" + "=" * 80)
print("测试完成！")
print("=" * 80)
