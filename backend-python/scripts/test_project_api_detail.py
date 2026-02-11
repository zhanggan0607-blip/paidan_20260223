import requests
import json

base_url = "http://localhost:8080/api/v1"

print("=" * 60)
print("测试项目信息 API 的详细请求和响应")
print("=" * 60)
print()

test_cases = [
    {
        "name": "默认请求（无参数）",
        "url": "/project-info?page=0&size=10",
        "description": "前端默认请求"
    },
    {
        "name": "请求第1页（page=0）",
        "url": "/project-info?page=0&size=10",
        "description": "明确指定第1页"
    },
    {
        "name": "请求第2页（page=1）",
        "url": "/project-info?page=1&size=10",
        "description": "明确指定第2页"
    },
    {
        "name": "请求更多数据（page=0&size=100）",
        "url": "/project-info?page=0&size=100",
        "description": "请求更多数据"
    }
]

for test in test_cases:
    print(f"\n{'=' * 60}")
    print(f"测试: {test['name']}")
    print(f"URL: {base_url}{test['url']}")
    print(f"说明: {test['description']}")
    print("=" * 60)
    
    try:
        response = requests.get(f"{base_url}{test['url']}")
        print(f"HTTP 状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应 code: {data.get('code')}")
            print(f"响应 message: {data.get('message')}")
            
            if 'data' in data:
                response_data = data['data']
                print(f"\n响应数据结构:")
                print(f"  data 类型: {type(response_data)}")
                print(f"  data 键: {list(response_data.keys())}")
                
                if 'content' in response_data:
                    items = response_data['content']
                    print(f"  content 类型: {type(items)}")
                    print(f"  content 长度: {len(items)}")
                    print(f"  totalElements: {response_data.get('totalElements', 'N/A')}")
                    print(f"  totalPages: {response_data.get('totalPages', 'N/A')}")
                    
                    if items:
                        print(f"\n  前5条记录:")
                        for i, item in enumerate(items[:5]):
                            print(f"    {i+1}. ID: {item.get('id')}, 项目编号: {item.get('project_id')}, 项目名称: {item.get('project_name')}")
                elif isinstance(response_data, list):
                    print(f"  data 是列表，长度: {len(response_data)}")
                    if response_data:
                        print(f"\n  前5条记录:")
                        for i, item in enumerate(response_data[:5]):
                            print(f"    {i+1}. ID: {item.get('id')}, 项目编号: {item.get('project_id')}, 项目名称: {item.get('project_name')}")
        else:
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"请求失败: {str(e)}")
    
    print()