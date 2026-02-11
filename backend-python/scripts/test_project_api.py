import requests
import json

url = "http://localhost:8080/api/v1/project-info?page=0&size=10"
headers = {"Content-Type": "application/json"}

try:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API 请求成功")
        print(f"响应数据:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"❌ API 请求失败: {response.status_code} - {response.text}")
except Exception as e:
    print(f"❌ 请求异常: {str(e)}")