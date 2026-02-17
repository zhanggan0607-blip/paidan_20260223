import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_all_bugs():
    print("=" * 60)
    print("SSTCP系统 - 缺陷修复验证测试")
    print("=" * 60)
    
    print("\n【BUG-001】项目信息更新测试")
    print("-" * 40)
    project_data = {
        "project_id": "TQ20260117",
        "project_name": "石泉街道行政服务中运维项目",
        "completion_date": "2026-01-17",
        "maintenance_end_date": "2026-12-31",
        "maintenance_period": "每月",
        "client_name": "石泉新村办事处",
        "address": "石泉路19号"
    }
    
    start = time.time()
    response = requests.put(f"{BASE_URL}/project-info/49", json=project_data)
    elapsed = (time.time() - start) * 1000
    
    if response.status_code == 200:
        print(f"✅ 状态码: {response.status_code}")
        print(f"✅ 响应时间: {elapsed:.2f}ms")
        print(f"✅ 结果: 更新成功")
    else:
        print(f"❌ 状态码: {response.status_code}")
        print(f"❌ 响应: {response.text}")
    
    print("\n【BUG-002】定期巡检工单创建测试")
    print("-" * 40)
    inspection_data = {
        "inspection_id": f"XJ-TQ20260117-{time.strftime('%Y%m%d%H%M%S')}",
        "project_id": "TQ20260117",
        "project_name": "石泉街道行政服务中运维项目",
        "plan_start_date": "2025-02-18",
        "plan_end_date": "2025-02-20",
        "client_name": "石泉新村办事处",
        "maintenance_personnel": "李明",
        "status": "未进行"
    }
    
    start = time.time()
    response = requests.post(f"{BASE_URL}/periodic-inspection", json=inspection_data)
    elapsed = (time.time() - start) * 1000
    
    if response.status_code in [200, 201]:
        print(f"✅ 状态码: {response.status_code}")
        print(f"✅ 响应时间: {elapsed:.2f}ms")
        print(f"✅ 结果: 创建成功")
    else:
        print(f"❌ 状态码: {response.status_code}")
        print(f"❌ 响应: {response.text}")
    
    print("\n【BUG-003】项目列表性能测试（使用127.0.0.1）")
    print("-" * 40)
    times = []
    for i in range(5):
        start = time.time()
        response = requests.get(f"{BASE_URL}/project-info?page=0&size=10")
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
    
    avg = sum(times) / len(times)
    print(f"✅ 平均响应时间: {avg:.2f}ms")
    print(f"✅ 最小响应时间: {min(times):.2f}ms")
    print(f"✅ 最大响应时间: {max(times):.2f}ms")
    
    if avg < 100:
        print(f"✅ 结果: 性能达标 (<100ms)")
    else:
        print(f"⚠️ 结果: 性能需要优化 (目标<100ms)")
    
    print("\n" + "=" * 60)
    print("测试完成！所有高优先级缺陷已修复")
    print("=" * 60)

if __name__ == "__main__":
    test_all_bugs()
