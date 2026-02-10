import requests
import json

base_url = "http://localhost:8080/api/v1"

print("测试分页查询...")
response = requests.get(f"{base_url}/personnel?page=0&size=10", timeout=10)
print(f"状态码: {response.status_code}")
print(f"响应内容: {response.text}")
