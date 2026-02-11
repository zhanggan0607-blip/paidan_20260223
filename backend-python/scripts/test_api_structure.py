import requests
import json

url = "http://localhost:8080/api/v1/project-info?page=0&size=10"
headers = {"Content-Type": "application/json"}

try:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API 请求成功")
        print(f"\n返回的数据结构:")
        print(f"  - code: {data.get('code')}")
        print(f"  - message: {data.get('message')}")
        print(f"  - data keys: {data.get('data', {}).keys()}")
        
        items = data.get('data', {}).get('content', [])
        print(f"\n第一条记录的完整字段:")
        if items:
            first_item = items[0]
            for key, value in first_item.items():
                print(f"  {key}: {value} (type: {type(value).__name__})")
    else:
        print(f"❌ API 请求失败: {response.status_code} - {response.text}")
except Exception as e:
    print(f"❌ 请求异常: {str(e)}")