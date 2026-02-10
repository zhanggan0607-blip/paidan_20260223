import time
import requests

print("=" * 80)
print("项目性能测试")
print("=" * 80)

base_url = "http://localhost:8080/api/v1"

print("\n1. 测试 API 响应时间...")
endpoints = [
    ('GET', f'{base_url}/project-info/all/list'),
    ('GET', f'{base_url}/personnel/all/list'),
    ('GET', f'{base_url}/periodic-inspection/all/list'),
    ('GET', f'{base_url}/maintenance-plan/all/list'),
]

for method, url in endpoints:
    try:
        start_time = time.time()
        if method == 'GET':
            response = requests.get(url, timeout=10)
        else:
            response = requests.post(url, json={}, timeout=10)
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        
        status = '✅' if response.status_code == 200 else '❌'
        print(f"   {status} {method} {url.split('/')[-2]}: {response_time:.2f}ms (状态码: {response.status_code})")
    except Exception as e:
        print(f"   ❌ {method} {url.split('/')[-2]}: 错误 - {str(e)}")

print("\n2. 测试数据库查询性能...")
try:
    import psycopg2
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="tq",
        user="postgres",
        password="123456"
    )
    cursor = conn.cursor()
    
    queries = [
        ("SELECT COUNT(*) FROM project_info", "项目信息计数"),
        ("SELECT COUNT(*) FROM maintenance_plan", "维保计划计数"),
        ("SELECT COUNT(*) FROM personnel", "人员计数"),
        ("SELECT COUNT(*) FROM periodic_inspection", "定期巡检单计数"),
        ("SELECT * FROM project_info LIMIT 10", "项目信息查询"),
        ("SELECT * FROM personnel LIMIT 10", "人员查询"),
    ]
    
    for query, description in queries:
        start_time = time.time()
        cursor.execute(query)
        end_time = time.time()
        query_time = (end_time - start_time) * 1000
        print(f"   ✅ {description}: {query_time:.2f}ms")
    
    conn.close()
except Exception as e:
    print(f"   ❌ 数据库查询错误: {str(e)}")

print("\n3. 测试前端构建性能...")
try:
    import subprocess
    start_time = time.time()
    result = subprocess.run(
        ['npm', 'run', 'build'],
        cwd='d:\\共享文件\\SSTCP-paidan260120',
        capture_output=True,
        text=True,
        timeout=60
    )
    end_time = time.time()
    build_time = (end_time - start_time) * 1000
    
    if result.returncode == 0:
        print(f"   ✅ 前端构建: {build_time:.2f}ms")
    else:
        print(f"   ❌ 前端构建失败: {result.stderr}")
except Exception as e:
    print(f"   ❌ 前端构建错误: {str(e)}")

print("\n" + "=" * 80)
print("✅ 性能测试完成！")
print("=" * 80)
