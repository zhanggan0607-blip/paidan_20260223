import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_project_update():
    print("=" * 50)
    print("测试 BUG-001: 更新项目信息")
    print("=" * 50)
    
    project_data = {
        "project_id": "TQ20260117",
        "project_name": "石泉街道行政服务中运维项目",
        "completion_date": "2026-01-17",
        "maintenance_end_date": "2026-12-31",
        "maintenance_period": "每月",
        "client_name": "石泉新村办事处",
        "address": "石泉路19号"
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/project-info/49",
            json=project_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"错误: {str(e)}")

def test_periodic_inspection_create():
    print("\n" + "=" * 50)
    print("测试 BUG-002: 创建定期巡检工单（使用真实人员）")
    print("=" * 50)
    
    inspection_data = {
        "inspection_id": "XJ-TQ20260117-20250218",
        "project_id": "TQ20260117",
        "project_name": "石泉街道行政服务中运维项目",
        "plan_start_date": "2025-02-18",
        "plan_end_date": "2025-02-20",
        "client_name": "石泉新村办事处",
        "maintenance_personnel": "李明",
        "status": "未进行"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/periodic-inspection",
            json=inspection_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"错误: {str(e)}")

def test_project_list_performance():
    print("\n" + "=" * 50)
    print("测试 BUG-003: 项目列表性能")
    print("=" * 50)
    
    import time
    start = time.time()
    try:
        response = requests.get(f"{BASE_URL}/project-info?page=0&size=10")
        elapsed = (time.time() - start) * 1000
        print(f"状态码: {response.status_code}")
        print(f"响应时间: {elapsed:.2f}ms")
        if response.status_code == 200:
            data = response.json()
            print(f"总记录数: {data.get('data', {}).get('total', 0)}")
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    test_project_update()
    test_periodic_inspection_create()
    test_project_list_performance()
